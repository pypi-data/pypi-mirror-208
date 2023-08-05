<template>
  <v-select
    v-if="availableLanguages"
    v-model="language"
    :items="availableLanguages"
    :item-text="nameForMenu"
    item-value="code"
    menu-props="auto"
    outlined
    color="primary"
    hide-details="auto"
    single-line
    return-object
    dense
    style="width: 75px"
    @input="setLanguage(language)"
  >
    <template #selection="{ item, index }">
      <span class="text-uppercase">{{ item.code }}</span>
    </template>
  </v-select>
</template>

<script>
export default {
  data: function () {
    return {
      language: this.$i18n.locale,
    };
  },
  props: {
    availableLanguages: {
      type: Array,
      required: true,
    },
  },
  methods: {
    setLanguage: function (languageOption) {
      document.cookie = languageOption.cookie;
      this.$i18n.locale = languageOption.code;
      this.$vuetify.lang.current = languageOption.code;
    },
    nameForMenu: function (item) {
      return `${item.nameLocal} (${item.code})`;
    },
  },
  name: "LanguageForm",
};
</script>
