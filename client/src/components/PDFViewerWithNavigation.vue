<template>
  <div :class="['col-span-12', hasAnswerScheme ? 'lg:col-span-3' : 'lg:col-span-6']">
    <div class="border rounded-lg bg-white shadow">
      <div class="p-4 border-b font-medium">Question Paper</div>
      <div v-if="fileURL" class="h-[calc(100vh-200px)]">
        <div class="h-full relative overflow-y-scroll">
          <div class="flex justify-center items-center">
            <PDFViewer :ref="id + '-ref'" :id="id" :file-name="fileName" :scale="localScale" :current-page="currentPage"
              :fileURL="fileURL" @total-pages="initTotalPages" :is-search-input-visible="isSearchInputVisible"
              @close-search-input="isSearchInputVisible = false">
              <template #header>
                <slot name="header"></slot>
              </template>
            </PDFViewer>
          </div>
          <div class="sticky bottom-0 left-0 right-0 z-[1020] bg-white border-t shadow-lg">
            <DocNavigation :id="id" :currentPage="currentPage"
              :totalPages="totalPages" @page-changed="handleInputPageChanged" @next-page="nextPage"
              @previous-page="previousPage" @zoom-in="zoomIn" @zoom-out="zoomOut" 
              @search-text="triggerSearch" />
          </div>
        </div>
      </div>
      <div v-else class="h-[calc(100vh-200px)] flex items-center justify-center rounded-md bg-gray-100 text-gray-400">
        PDF Preview
      </div>
    </div>
  </div>
</template>

<script>
import PDFViewer from '@/components/PDFViewer.vue';
import DocNavigation from '@/components/DocNavigation.vue';

export default {
  name: 'PDFViewerWithNavigation',
  components: {
    PDFViewer,
    DocNavigation
  },
  data() {
    return {
      currentPage: 1,
      totalPages: 0,
      localScale: this.scale || 0.9,
      pdfWidth: null,
      containerWidth: 0,

      cancelUpdateThroughScroll: false,
      cancelUpdateTimeout: null,

      isSearchInputVisible: false,
    }
  },
  props: {
    documentDetail: {
      type: Object,
      required: true
    },
    id: {
      type: String,
      required: true
    },
    fileName: {
      type: String,
      default: ''
    },
    fileURL: {
      type: String,
      required: true
    },
    scale: {
      type: Number,
      default: null
    },
    autoFit: {
      type: Boolean,
      default: false
    },
    gotoPage: {
      type: Number,
      default: null
    }
  },
  mounted() {
    if (this.autoFit) {
      this.calculateScale();
      window.addEventListener('resize', this.calculateScale);
    }

    // Handle gotoPage prop when component mounts
    if (this.gotoPage && this.gotoPage > 0) {
      // Wait a bit for the PDF to load and initialize
      setTimeout(() => {
        this.handleInputPageChanged(this.gotoPage);
      }, 500);
    }
  },
  beforeUnmount() {
    if (this.autoFit) {
      window.removeEventListener('resize', this.calculateScale);
    }
  },
  methods: {
    calculateScale() {
      const container = this.$el;
      if (container && this.pdfWidth) {
        const containerWidth = container.clientWidth;
        // Subtract some padding to account for margins/borders
        const availableWidth = containerWidth - 40;
        this.localScale = availableWidth / this.pdfWidth;
      }
    },
    initTotalPages(pages) {
      this.totalPages = pages;
      // Get PDF dimensions after it's loaded
      this.$nextTick(async () => {
        const pdfViewer = this.$refs[this.id + '-ref'];
        if (pdfViewer && pdfViewer.pdfDocument) {
          const page = await pdfViewer.pdfDocument.getPage(1);
          const viewport = page.getViewport({ scale: 1 });
          this.pdfWidth = viewport.width;
          if (this.autoFit) {
            this.calculateScale();
          }
        }
      });
    },
    zoomIn() {
      this.localScale = Math.min(this.localScale + 0.05, 2);
    },
    zoomOut() {
      this.localScale = Math.max(this.localScale - 0.05, 0.5);
    },
    triggerSearch() {
      this.isSearchInputVisible = true;
      this.$nextTick(() => {
        this.$refs[this.id + '-ref'].focusSearchInput();
      });
    },

    updateCurrentPage() {
      const pdfViewer = this.$refs[this.id + '-ref'];
      if (pdfViewer) {
        const pages = pdfViewer.$refs;
        for (let i = 1; i <= this.totalPages; i++) {
          const pageElement = pages[`page-${i}`];
          if (pageElement && pageElement[0]) {
            const rect = pageElement[0].getBoundingClientRect();
            const threshold = window.innerHeight * 1; // Scroll detection area value
            if (rect.top >= -threshold && rect.bottom <= window.innerHeight + threshold) {
              this.currentPage = i;
              break;
            }
          }
        }
      }
    },

    nextPage(page) {
      this.cancelUpdateThroughScroll = true;
      this.currentPage = page;
      this.$refs[this.id + '-ref'].scrollToPage(this.currentPage);
      this.setCancelUpdateThroughScrollToFalse();
    },
    previousPage(page) {
      this.cancelUpdateThroughScroll = true;
      this.currentPage = page;
      this.$refs[this.id + '-ref'].scrollToPage(this.currentPage);
      this.setCancelUpdateThroughScrollToFalse();
    },
    handleInputPageChanged(page) {
      this.cancelUpdateThroughScroll = true;
      this.$refs[this.id + '-ref'].scrollToPage(page);
      this.setCancelUpdateThroughScrollToFalse();
    },

    setCancelUpdateThroughScrollToFalse() {
      clearTimeout(this.cancelUpdateTimeout)
      this.cancelUpdateTimeout = setTimeout(() => {
        this.cancelUpdateThroughScroll = false;
      }, 1000);
    },
  }
}
</script>