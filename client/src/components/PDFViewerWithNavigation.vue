<template>
  <div
    class="tw-w-full tw-overflow-y-auto position-relative tw-shadow-md"
    @scroll="handleScroll"
  >
    <div class="tw-flex tw-justify-center tw-items-center">
      <PDFViewer
        :ref="id + '-ref'"
        :id="id"
        :file-name="fileName"
        :scale="localScale" 
        :current-page="currentPage"
        :fileURL="fileURL"
        @total-pages="initTotalPages"
        :is-search-input-visible="isSearchInputVisible"
        @close-search-input="isSearchInputVisible = false"
      >
        <template #header>
          <slot name="header"></slot>
        </template>
      </PDFViewer>
    </div>
    <div
      class="tw-max-w-fit tw-p-5 tw-mx-auto tw-sticky tw-bottom-0 tw-z-[1020] tw-mb-6"
      @mouseenter="handleMouseEnter" 
      @mouseleave="handleMouseLeave"
    >
      <DocNavigation
        :id="id"
        class="tw-relative tw--bottom-32 tw-transition-all tw-duration-300"
        :class="{ 'bottom-0': isHovered || isScrolling }"
        :currentPage="currentPage"
        :totalPages="totalPages"
        @page-changed="handleInputPageChanged"
        @next-page="nextPage"
        @previous-page="previousPage"
        @zoom-in="zoomIn"
        @zoom-out="zoomOut"
        @search-text="triggerSearch"
      />
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
      localScale: this.scale,

      isScrolling: false,
      isHovered: false,
      scrollTimeout: null,
      cancelUpdateThroughScroll: false,
      cancelUpdateTimeout: null,

      isSearchInputVisible: false,
    }
  },
  props: {
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
      default: 0.8
    },
  },
  methods: {
    initTotalPages(pages) {
      this.totalPages = pages;
    },
    zoomIn() {
      this.localScale = Math.min(this.localScale + 0.1, 2); 
    },
    zoomOut() {
      this.localScale = Math.max(this.localScale - 0.1, 0.5);
    },
    triggerSearch() {
      this.isSearchInputVisible = true;
      this.$nextTick(() => {
        this.$refs[this.id + '-ref'].focusSearchInput();
      });
    },

    // scroll handling
    handleScroll() {
      this.isScrolling = true;
      this.hoverTimeout();
      if (this.cancelUpdateThroughScroll) return;
      this.updateCurrentPage();
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

    // page navigation
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

    // navigator mouse events
    handleMouseEnter() {
      this.isHovered = true;
      clearTimeout(this.scrollTimeout);
    },
    handleMouseLeave() {
      this.isHovered = false;
      this.hoverTimeout();
    },

    // utilities
    hoverTimeout() {
      if (!this.isHovered) {
        clearTimeout(this.scrollTimeout);
        this.scrollTimeout = setTimeout(() => {
          this.isScrolling = false;
        }, 1000);
      }
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