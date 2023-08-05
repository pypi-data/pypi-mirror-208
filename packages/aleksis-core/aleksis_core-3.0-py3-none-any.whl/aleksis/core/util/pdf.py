import base64
import os
import subprocess  # noqa
from datetime import timedelta
from tempfile import TemporaryDirectory
from typing import Callable, Optional, Tuple, Union
from urllib.parse import urljoin

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext as _

from celery.result import AsyncResult
from celery_progress.backend import ProgressRecorder
from selenium import webdriver

from aleksis.core.celery import app
from aleksis.core.models import PDFFile
from aleksis.core.util.celery_progress import recorded_task, render_progress_page
from aleksis.core.util.core_helpers import has_person, process_custom_context_processors


def _generate_pdf_with_chromium(temp_dir, pdf_path, html_url, lang):
    """Generate a PDF file from a HTML file."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--kiosk-printing")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--dbus-stub")
    chrome_options.add_argument("--temp-profile")
    chrome_options.add_argument(f"--lang={lang}")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(html_url)
    pdf = driver.execute_cdp_cmd(
        "Page.printToPDF", {"printBackground": True, "preferCSSPageSize": True}
    )
    driver.close()
    with open(pdf_path, "wb") as f:
        f.write(base64.b64decode(pdf["data"]))


@recorded_task
def generate_pdf(
    file_pk: int, html_url: str, recorder: ProgressRecorder, lang: Optional[str] = None
):
    """Generate a PDF file by rendering the HTML code using a headless Chromium."""
    file_object = get_object_or_404(PDFFile, pk=file_pk)

    recorder.set_progress(0, 1)

    # Open a temporary directory
    with TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, "print.pdf")
        lang = lang or get_language()

        _generate_pdf_with_chromium(temp_dir, pdf_path, html_url, lang)

        # Upload PDF file to media storage
        with open(pdf_path, "rb") as f:
            file_object.file.save("print.pdf", File(f))
            file_object.save()

    recorder.set_progress(1, 1)


def process_context_for_pdf(context: Optional[dict] = None, request: Optional[HttpRequest] = None):
    context = context or {}
    if not request:
        processed_context = process_custom_context_processors(
            settings.NON_REQUEST_CONTEXT_PROCESSORS
        )
        processed_context.update(context)
    else:
        processed_context = context
    return processed_context


def generate_pdf_from_html(
    html: str, request: Optional[HttpRequest] = None, file_object: Optional[PDFFile] = None
) -> Tuple[PDFFile, AsyncResult]:
    """Start a PDF generation task and return the matching file object and Celery result."""
    html_file = ContentFile(html.encode(), name="source.html")

    # In some cases, the file object is already created (to get a redirect URL for the PDF)
    if not file_object:
        file_object = PDFFile.objects.create()
    if request and has_person(request):
        file_object.person = request.user.person
    file_object.html_file = html_file
    file_object.save()

    # As this method may be run in background and there is no request available,
    # we have to use a predefined URL from settings then
    if request:
        html_url = request.build_absolute_uri(file_object.html_file.url)
    else:
        html_url = urljoin(settings.BASE_URL, file_object.html_file.url)

    result = generate_pdf.delay(file_object.pk, html_url, lang=get_language())

    return file_object, result


def generate_pdf_from_template(
    template_name: str,
    context: Optional[dict] = None,
    request: Optional[HttpRequest] = None,
    render_method: Optional[Callable] = None,
    file_object: Optional[PDFFile] = None,
) -> Tuple[PDFFile, AsyncResult]:
    """Start a PDF generation task and return the matching file object and Celery result."""
    processed_context = process_context_for_pdf(context, request)

    if render_method:
        html_template = render_method(processed_context, request)
    else:
        html_template = render_to_string(template_name, processed_context, request)

    return generate_pdf_from_html(html_template, request, file_object=file_object)


def render_pdf(
    request: Union[HttpRequest, None], template_name: str, context: dict = None
) -> HttpResponse:
    """Start PDF generation and show progress page.

    The progress page will redirect to the PDF after completion.
    """
    if not context:
        context = {}

    file_object, result = generate_pdf_from_template(template_name, context, request)

    redirect_url = f"/pdfs/{file_object.pk}"

    return render_progress_page(
        request,
        result,
        title=_("Progress: Generate PDF file"),
        progress_title=_("Generating PDF file …"),
        success_message=_("The PDF file has been generated successfully."),
        error_message=_("There was a problem while generating the PDF file."),
        redirect_on_success_url=redirect_url,
        back_url=context.get("back_url", reverse("index")),
        button_title=_("Download PDF"),
        button_url=redirect_url,
        button_icon="mdi-file-pdf-box",
    )


def clean_up_expired_pdf_files() -> None:
    """Clean up expired PDF files."""
    PDFFile.objects.filter(expires_at__lt=timezone.now()).delete()


@app.task(run_every=timedelta(days=1))
def clean_up_expired_pdf_files_task() -> None:
    """Clean up expired PDF files."""
    return clean_up_expired_pdf_files()
