// Configuration for Vite bundling
//
// This config is somewhat elaborate, because it needs to dynamically address
// the several environments where it is used. The AlekSIS frontend bundle is
// always created as a custom asset for a given Django deployment, in order
// to allow for dynamic addition of frontend code from AlekSIS apps.
//
// It is therefore also placed inside the Python package structure, so it
// will be installed into the target system/image by poetry.
//
// Hence, the main scenarios are:
//
//  * called directly from the source tree of AlekSIS-Core, with
//    cache dir (and thus node_module) in ./cache
//  * called from basically anywhere, with the cace dir also anywhere
//
// Vite must always be called through the `aleksis-admin vite` wrapper, which
// generates a JSON file with some hints in the cache directory, so we can
// make Vite find all the puzzle pieces.

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const process = require("process");

import { defineConfig, searchForWorkspaceRoot } from "vite";
import vue from "@vitejs/plugin-vue2";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import graphql from "@rollup/plugin-graphql";
import virtual from "@rollup/plugin-virtual";
import { VitePWA } from "vite-plugin-pwa";
import topLevelAwait from "vite-plugin-top-level-await";
import browserslistToEsbuild from "browserslist-to-esbuild";
const license = require("rollup-plugin-license");

// Read the hints writen by `aleksis-admin vite`
const django_values = JSON.parse(fs.readFileSync("./django-vite-values.json"));

// Browsers supported by us
const browsersList = [
  "defaults and supports es6-module",
  ">0.2% in de and supports es6-module",
];

/**
 * Generate code to import messages from a single AlekSIS app.
 */
function generateMessageImportCode(assetDir, name, importAppName) {
  let code = "";
  let messagesPath = assetDir + "/messages/";
  code += `appMessages["${name}"] = {};`;
  const files = fs.readdirSync(messagesPath);
  for (file of files) {
    let lang = file.split(".")[0];
    code += `import ${importAppName}Messages_${lang} from '${
      messagesPath + file
    }';\n`;
    code += `appMessages["${name}"]["${lang}"] = ${importAppName}Messages_${lang};\n`;
  }
  return code;
}

/**
 * Generate a virtual module that helps the AlekSIS-Core frontend code import other apps.
 *
 * App code locations are discovered by the `aleksis-admin` vite wrapper and passed
 * in the django_values hints.
 */
function generateAppImporter(appDetails) {
  let code = "let appObjects = {};\n";
  code += "let appMessages = {};\n";

  for (const [appPackage, appMeta] of Object.entries(appDetails)) {
    let indexPath = appMeta.assetDir + "/index.js";
    let importAppName =
      appMeta.name.charAt(0).toUpperCase() + appMeta.name.substring(1);

    code += `console.debug("Importing AlekSIS app entrypoint for ${appPackage}");\n`;
    code += `import ${importAppName} from '${indexPath}';\n`;
    code += `appObjects["${appMeta.name}"] = ${importAppName};\n`;

    if (appMeta.hasMessages) {
      code += generateMessageImportCode(
        appMeta.assetDir,
        appMeta.name,
        importAppName
      );
    }
  }

  // Include core messages
  code += generateMessageImportCode(django_values.coreAssetDir, "core", "Core");

  code += "export default appObjects;\n";
  code += "export { appObjects, appMessages };\n";

  return code;
}

export default defineConfig({
  // root must always be the base directory of the AlekSIS-Core source tree
  //  Changing this will mangle the manifest key of the entrypoint!
  root: django_values.baseDir,
  // Base URL needs to mimic the /static/ URL in Django
  base: django_values.static_url,
  build: {
    outDir: path.resolve("./vite_bundles/"),
    manifest: true,
    target: browserslistToEsbuild(browsersList),
    rollupOptions: {
      input: django_values.coreAssetDir + "/index.js",
      output: {
        manualChunks(id) {
          // Split big libraries into own chunks
          if (id.includes("node_modules/vue")) {
            return "vue";
          } else if (id.includes("node_modules/apollo")) {
            return "apollo";
          } else if (id.includes("node_modules/graphql")) {
            return "graphql";
          } else if (id.includes("node_modules/@sentry")) {
            return "sentry";
          } else if (id.includes("node_modules")) {
            // Fallback for all other libraries
            return "vendor";
          }

          // Split each AlekSIS app in its own chunk
          for (const [appPackage, ad] of Object.entries(
            django_values.appDetails
          )) {
            if (id.includes(ad.assetDir + "/index.js")) {
              return appPackage;
            }
          }
        },
      },
    },
  },
  server: {
    strictPort: true,
    port: django_values.serverPort,
    origin: `http://localhost:${django_values.serverPort}`,
    watch: {
      ignored: [
        "**/*.py",
        "**/__pycache__/**",
        "**/*.mo",
        "**/.venv/**",
        "**/.tox/**",
        "**/static/**",
        "**/assets/**",
      ],
    },
    fs: {
      allow: [
        searchForWorkspaceRoot(path.resolve(django_values.baseDir)),
        ...Object.values(django_values.appDetails).map(
          (details) => details.assetDir
        ),
      ],
    },
  },
  plugins: [
    virtual({
      // Will be used in AlekSIS-Core frontend code to import aps
      aleksisAppImporter: generateAppImporter(django_values.appDetails),
    }),
    vue(),
    nodeResolve({ modulePaths: [path.resolve(django_values.node_modules)] }),
    graphql(),
    topLevelAwait(),
    license({
      // A package.json will be written here by `aleksis-admin vite`
      cwd: path.resolve(django_values.cacheDir),
      banner: {
        commentStyle: "ignored",
        content: `Frontend bundle for AlekSIS\nSee ./vendor.LICENSE.txt for copyright information.`,
      },
      thirdParty: {
        allow: {
          test: "MIT OR Apache-2.0 OR 0BSD OR BSD-3-Clause",
          failOnUnlicensed: true,
          failOnViolation: true,
        },
        output: {
          file: path.resolve(
            django_values.cacheDir + "/vite_bundles/assets/vendor.LICENSE.txt"
          ),
        },
      },
    }),
    VitePWA({
      injectRegister: "null",
      devOptions: {
        enabled: true,
      },
      scope: "/",
      base: "/",
      workbox: {
        navigateFallback: "/",
        directoryIndex: null,
        navigateFallbackAllowlist: [
          new RegExp("^/(?!(django|admin|graphql|__icons__))[^.]*$"),
        ],
        additionalManifestEntries: [
          { url: "/", revision: crypto.randomUUID() },
          { url: "/django/offline/", revision: crypto.randomUUID() },
        ],
        inlineWorkboxRuntime: true,
        modifyURLPrefix: {
          "": "/static/",
        },
        globPatterns: ["**/*.{js,css,eot,woff,woff2,ttf}"],
        runtimeCaching: [
          {
            urlPattern: new RegExp(
              "^/(?!(django|admin|graphql|__icons__))[^.]*$"
            ),
            handler: "CacheFirst",
          },
          {
            urlPattern: new RegExp("/django/.*"),
            handler: "NetworkFirst",
            options: {
              cacheName: "aleksis-legacy-cache",
              networkTimeoutSeconds: 5,
              expiration: {
                maxAgeSeconds: 60 * 60 * 24,
              },
              precacheFallback: {
                fallbackURL: "/django/offline/",
              },
              cacheableResponse: {
                headers: {
                  "PWA-Is-Cacheable": "true",
                },
              },
              plugins: [
                {
                  fetchDidSucceed: async ({ request, response }) => {
                    if (response.status < 500) {
                      return response;
                    }
                    throw new Error(
                      `${response.status} ${response.statusText}`
                    );
                  },
                },
              ],
            },
          },
          {
            urlPattern: ({ request, sameOrigin }) => {
              return sameOrigin && request.destination === "image";
            },
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "aleksis-image-cache",
              expiration: {
                maxAgeSeconds: 60 * 60 * 24,
              },
            },
          },
          {
            urlPattern: ({ request, sameOrigin }) => {
              return sameOrigin && request.destination === "style";
            },
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "aleksis-style-cache",
              expiration: {
                maxAgeSeconds: 60 * 60 * 24 * 30,
              },
            },
          },
          {
            urlPattern: ({ request, sameOrigin }) => {
              return sameOrigin && request.destination === "script";
            },
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "aleksis-script-cache",
              expiration: {
                maxAgeSeconds: 60 * 60 * 24 * 30,
              },
            },
          },
          {
            urlPattern: ({ request, sameOrigin }) => {
              return sameOrigin && request.destination === "font";
            },
            handler: "CacheFirst",
            options: {
              cacheName: "aleksis-font-cache",
              expiration: {
                maxAgeSeconds: 60 * 60 * 24 * 90,
              },
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(django_values.node_modules),
      vue: path.resolve(django_values.node_modules + "/vue/dist/vue.esm.js"),
      "aleksis.core": django_values.coreAssetDir,
      // Add aliases for every app using their package name
      ...Object.fromEntries(
        Object.entries(django_values.appDetails).map(([name, appMeta]) => [
          name,
          appMeta.assetDir,
        ])
      ),
    },
  },
});
