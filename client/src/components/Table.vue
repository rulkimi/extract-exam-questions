<template>
  <div class="overflow-x-auto w-full">
    <table style="border-collapse: collapse; table-layout: fixed; width: 100%;">
      <thead
        :class="striped ? 'border-b-2 bg-slate-100' : ''"
        v-if="!hideHeader"
      >
        <tr class="text-left">
          <th
            v-for="header in headers"
            :key="header.key"
            class="py-2 px-2 text-sm text-slate-600 font-bold"
            :class="header.cssClass"
            :width="header.width"
          >
            {{ header.label }}
          </th>
        </tr>
      </thead>
      <tbody v-if="loading">
        <tr>
          <td
            :colspan="headers.length"
            class="text-sm text-center pb-3 pt-6 text-slate-400 w-full"
          >
            <div class="flex justify-center">
              <Spinner size="large" />
            </div>
          </td>
        </tr>
      </tbody>
      <tbody v-else-if="!grouped">
        <!-- desktop view -->
        <tr
          v-for="(item, index) in data"
          :key="item.id + '-' + index"
          @click="handleRowClick(item)"
          class="border-b last:border-none border-slate-300"
          :class="[
            striped && 'even:bg-slate-100',
            clickableRow &&
              'cursor-pointer hover:bg-slate-100',
          ]"
        >
          <td
            v-for="header in headers"
            :key="header.key"
            class="py-2 px-2 text-sm text-slate-600 font-regular break-words"
            :align="header.align"
            :valign="header.valign ?? 'top'"
            :class="[ border && 'border border-slate-300']"
            :width="header.width"
          >
            <div v-if="hasSlotCell" :class="header.itemClass">
              <slot
                name="cell-content"
                :rowData="item"
                :header="header"
                :rowIndex="index"
              ></slot>
            </div>
            <div :class="header.itemClass" v-else>
              {{ item[header.key] }}
            </div>
          </td>
        </tr>

        <!-- mobile view -->
        <!-- <template v-else>
          <tr
            v-for="(item, j) in data"
            :key="item.id + '-' + j"
            @click="handleRowClick(item)"
            class="even:bg-slate-100 border-b last:border-none border-slate-300 text-sm"
            :class="{
                'cursor-pointer hover:bg-slate-200':
                  clickableRow,
              }"
          >
            <template>
              <td
                class="flex text-sm"
                v-for="(field, ix) in headers"
                :class="field.label ? 'justify-between':'justify-center'"
              >
                <div
                  class="text-slate-600 font-bold p-2 flex w-1/2"
                  v-if="field.label"
                >
                  {{ field.label }}
                </div>
                <div
                  class="p-2"
                  :class="field.label ? 'flex justify-end text-end' : 'flex justify-center'"
                >
                  <div v-if="hasSlotCell" :class="field.itemClass">
                    <slot
                      name="cell-content"
                      :rowData="item"
                      :header="field"
                      :rowIndex="j"
                    ></slot>
                  </div>
                  <div v-else :class="field.itemClass">
                    {{ item[field.key] }}
                  </div>
                </div>
              </td>
            </template>
          </tr>
        </template> -->
        <tr v-if="data && !data.length">
          <td
            :colspan="headers.length"
            class="text-sm text-center py-3 text-slate-400"
          >
            {{ noResultStatement }}
          </td>
        </tr> 
      </tbody>

      <!-- Grouped / Expandable row -->
      <tbody v-else>
        <template v-for="(item, index) in data" :key="index">
          <tr
            @click="toggleExpand(index)"
            class="border-b border-slate-300 cursor-pointer hover:bg-slate-100 transition-colors duration-200"
          >
            <!-- Loop through headers to display parent data -->
            <td
              v-for="header in filteredHeaders"
              :key="header.key"
              class="py-2 px-2 text-sm text-slate-600 font-regular"
              :align="header.align"
              :valign="header.valign ?? 'top'"
              :width="header.width"
              :colspan="filteredHeaders.length === 1 ? headers.length : header.colspan" 
            >
              <div class="flex justify-between">
                <slot
                  v-if="hasParentSlotCell"
                  name="parent-cell-content"
                  :rowData="item"
                  :header="header"
                  :rowIndex="index"
                ></slot>
                <div v-else>
                  {{ item[header.key] }}
                </div>
                <font-awesome-icon 
                  :icon="['fas', 'chevron-down']" 
                  class="transition-transform duration-300"
                  :class="{'rotate-180': item.expanded}" 
                />
              </div>
            </td>
          </tr>
          <!-- Child Rows -->
          <tr
            v-if="expandable ? item.expanded : true"
            class="bg-slate-50"
            @click="handleRowClick(dataChild)"
            :class="clickableRow ? 'cursor-pointer hover:bg-slate-200' : '' "
            v-for="(dataChild, dataIndex) in item.results"
            :key="dataIndex"
          >
            <td
              v-for="(header, headerIndex) in headers"
              :key="header.key + '-' + headerIndex"
              class="py-2 px-2 text-sm text-slate-600 font-regular border-b"
              :align="header.align"
              :valign="header.valign ?? 'top'"
              style="word-wrap: break-word;"
            >
              <!-- Use slot if available -->
              <div v-if="hasSlotCell && !header.parent" :class="header.itemClass">
                <slot
                  name="cell-content"
                  :rowData="dataChild"
                  :header="header"
                  :rowIndex="dataIndex"
                ></slot>
              </div>
              <div v-else-if="!header.parent" :class="header.itemClass">
                {{ dataChild[header.key] }}
              </div>
            </td>
          </tr>
        </template>
        <tr v-if="data && !data.length">
          <td
            :colspan="headers.length"
            class="text-sm text-center py-3 text-slate-400"
          >
            {{ noResultStatement }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { useSlots, computed, defineEmits } from 'vue';
import Spinner from '@/components/Spinner.vue'; 

const emit = defineEmits(["row-click", "change", "edit", "error"]);
const props = defineProps({
  headers: {
    type: Array,
    default: () => [],
  },
  data: {
    type: Array,
    default: () => [],
    required: true,
  },
  hideHeader: {
    type: Boolean,
    default: false,
  },
  striped: {
    type: Boolean,
    default: false,
  },
  clickableRow: {
    type: Boolean,
    default: false,
  },
  grouped: {
    type: Boolean,
    default: false,
  },
  expandable: {
    type: Boolean,
    default: false,
  },
  border: {
    type: Boolean,
    default: false,
  },
  noResultStatement: {
    type: String,
    default: 'No result found'
  },
  loading: {
    type: Boolean,
    default: false,
  }
});

const slots = useSlots();
const hasSlotCell = computed(() => !!slots["cell-content"]);
const hasParentSlotCell = computed(() => !!slots["parent-cell-content"]);
const filteredHeaders = computed(() => props.headers.filter(header => header.parent));

const handleRowClick = (item) => {
  emit("row-click", item);
}

const toggleExpand = (index) => {
  props.data.forEach((item, idx) => {
    item.expanded = idx === index ? !item.expanded : false;
  });
}
</script>