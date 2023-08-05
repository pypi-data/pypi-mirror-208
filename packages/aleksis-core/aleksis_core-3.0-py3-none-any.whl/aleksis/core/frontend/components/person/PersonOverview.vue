<template>
  <object-overview :query="query" title-attr="fullName">
    <template #loading>
      <v-skeleton-loader type="article" />

      <v-row>
        <v-col cols="12" lg="4" v-for="idx in 3" :key="idx">
          <v-skeleton-loader type="card" />
        </v-col>
      </v-row>
    </template>
    <template #default="person">
      <detail-view>
        <template #avatarContent>
          <person-avatar-clickbox :id="id" />
        </template>

        <template #title>
          {{ person.firstName }} {{ person.lastName }}
        </template>

        <template #subtitle>
          {{ person.username }}
        </template>

        <template #actions="{ classes }">
          <person-actions :class="classes" :id="person.id" />
        </template>

        <div class="text-center my-5" v-text="person.description"></div>

        <v-row>
          <v-col cols="12" lg="4">
            <v-card class="mb-6">
              <v-card-title>{{ $t("person.details") }}</v-card-title>

              <v-list two-line>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon> mdi-account-outline</v-icon>
                  </v-list-item-icon>

                  <v-list-item-content>
                    <v-list-item-title>
                      {{ person.firstName }}
                      {{ person.additionalName }}
                      {{ person.lastName }}
                    </v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-divider inset />

                <v-list-item>
                  <v-list-item-icon>
                    <v-icon> mdi-human-non-binary</v-icon>
                  </v-list-item-icon>

                  <v-list-item-content>
                    <v-list-item-title>
                      {{ person.sex || "–" }}
                    </v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-divider inset />

                <v-list-item>
                  <v-list-item-icon>
                    <v-icon> mdi-map-marker-outline</v-icon>
                  </v-list-item-icon>

                  <v-list-item-content>
                    <v-list-item-title
                      >{{ person.street || "–" }}
                      {{ person.housenumber }}
                    </v-list-item-title>
                    <v-list-item-subtitle
                      >{{ person.postalCode }}
                      {{ person.place }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-divider inset />

                <v-list-item
                  :href="person.phoneNumber ? 'tel:' + person.phoneNumber : ''"
                >
                  <v-list-item-icon>
                    <v-icon> mdi-phone-outline</v-icon>
                  </v-list-item-icon>

                  <v-list-item-content>
                    <v-list-item-title>
                      {{ person.phoneNumber || "–" }}
                    </v-list-item-title>
                    <v-list-item-subtitle>
                      {{ $t("person.home") }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>

                <v-list-item
                  :href="
                    person.mobileNumber ? 'tel:' + person.mobileNumber : ''
                  "
                >
                  <v-list-item-action></v-list-item-action>

                  <v-list-item-content>
                    <v-list-item-title>
                      {{ person.mobileNumber || "–" }}
                    </v-list-item-title>
                    <v-list-item-subtitle>
                      {{ $t("person.mobile") }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-divider inset />

                <v-list-item
                  :href="person.email ? 'mailto:' + person.email : ''"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-email-outline</v-icon>
                  </v-list-item-icon>

                  <v-list-item-content>
                    <v-list-item-title>
                      {{ person.email || "–" }}
                    </v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-divider inset />

                <v-list-item>
                  <v-list-item-icon>
                    <v-icon> mdi-cake-variant-outline</v-icon>
                  </v-list-item-icon>

                  <v-list-item-content>
                    <v-list-item-title
                      >{{
                        !!person.dateOfBirth
                          ? $d(new Date(person.dateOfBirth), "short")
                          : "–"
                      }}
                    </v-list-item-title>
                    <v-list-item-subtitle
                      >{{ person.placeOfBirth }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-card>

            <additional-image :src="person.secondaryImageUrl" />
          </v-col>

          <v-col
            cols="12"
            md="6"
            lg="4"
            v-if="person.children.length || person.guardians.length"
          >
            <v-card v-if="person.children.length" class="mb-6">
              <v-card-title>{{ $t("person.children") }}</v-card-title>
              <person-collection :persons="person.children" />
            </v-card>
            <v-card v-if="person.guardians.length">
              <v-card-title>{{ $t("person.guardians") }}</v-card-title>
              <person-collection :persons="person.guardians" />
            </v-card>
          </v-col>

          <v-col
            cols="12"
            md="6"
            lg="4"
            v-if="person.memberOf.length || person.ownerOf.length"
          >
            <v-card v-if="person.memberOf.length" class="mb-6">
              <v-card-title>{{ $t("group.title_plural") }}</v-card-title>
              <group-collection :groups="person.memberOf" />
            </v-card>
            <v-card v-if="person.ownerOf.length">
              <v-card-title>{{ $t("group.ownership") }}</v-card-title>
              <group-collection :groups="person.ownerOf" />
            </v-card>
          </v-col>
        </v-row>
      </detail-view>
    </template>
  </object-overview>
</template>

<script>
import AdditionalImage from "./AdditionalImage.vue";
import GroupCollection from "../group/GroupCollection.vue";
import ObjectOverview from "../generic/ObjectOverview.vue";
import PersonActions from "./PersonActions.vue";
import PersonAvatarClickbox from "./PersonAvatarClickbox.vue";
import PersonCollection from "./PersonCollection.vue";

import gqlPersonOverview from "./personOverview.graphql";

export default {
  name: "PersonOverview",
  components: {
    AdditionalImage,
    GroupCollection,
    ObjectOverview,
    PersonActions,
    PersonAvatarClickbox,
    PersonCollection,
  },
  data() {
    return {
      query: gqlPersonOverview,
    };
  },
  props: {
    id: {
      type: String,
      required: false,
      default: null,
    },
  },
};
</script>

<style scoped></style>
