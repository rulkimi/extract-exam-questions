<template>
	<div v-if="pdf" class="flex flex-col items-center text-center">

		<!-- search word input -->
		<div class="sticky top-0 z-[1020] h-0 w-9/12">
			<div
				class="relative opacity-0 top-[-100px] transition-all duration-300 p-4 bg-black text-white rounded-md flex items-center"
				:class="{ 'opacity-100 top-[5px]' : isSearchInputVisible }"
			>
				<input
					v-model="highlightText"
					:id="id + '-highlightText'"
					type="text"
					class="form-input"
					style="height: 30px;"
					autocomplete="off"
				/>
				<span v-if="highlightCount > 0" class="text-white me-2">
					<div class="d-inline-flex">
						<span v-if="currentHighlightIndex !== -1">{{ currentHighlightIndex + 1 }}/</span>
						{{ highlightCount }}
						<span v-if="currentHighlightIndex === -1">&nbsp;found</span>
					</div>
				</span>
				<div class="flex items-center justify-between gap-4">
					<button
						class="p-1"
						:class="{ 'text-gray-500' : highlightCount === 0 || currentHighlightIndex <= 0 }"
						:disabled="highlightCount === 0 || currentHighlightIndex <= 0"
						@click="scrollToMatch('prev')"
					>
						<font-awesome-icon :icon="['fas', 'chevron-up']" />
					</button>
					<button
						class="p-1"
						:class="{ 'text-gray-500' : highlightCount === 0 || currentHighlightIndex >= totalMatches.length - 1 }"
						:disabled="highlightCount === 0 || currentHighlightIndex >= totalMatches.length - 1"
						@click="scrollToMatch('next')"
					>
						<font-awesome-icon :icon="['fas', 'chevron-down']" />
					</button>
					<button class="p-1" @click="closeSearchInput">
						<font-awesome-icon :icon="['fas', 'times']" />
					</button>
				</div>

			</div>
		</div>

		<!-- header: file name -->
		<div class="bg-white/50 border rounded-lg my-2 text-xs text-gray-400 p-2 sticky top-0 z-[10] w-full">
			<slot name="header">{{ fileName }}</slot>
		</div>

		<!-- PDF display -->
		<div v-for="page in pages" :key="page" class="mb-5" :ref="`page-${page}`">
			<VuePDF 
				:pdf="pdf"
				:page="page"
				:scale="scale"
				text-layer
				:highlight-text="highlightText"
				:highlight-options="highlightOptions"
				:highlight-index="currentHighlightIndex"
				@highlight="onHighlight"
			>
				<div class="flex justify-center items-center h-screen">
					<Spinner size="large" />
				</div>
			</VuePDF>
			<span class="text-gray-400 block mt-4">Page {{ page }}</span>
		</div>

	</div>
</template>

<script>
import { VuePDF, usePDF } from '@tato30/vue-pdf';
import '@tato30/vue-pdf/style.css';
import Spinner from '@/components/Spinner.vue';

export default {
	components: {
		VuePDF,
		Spinner
	},
	emits: ['page-changed', 'total-pages', 'close-search-input'],
	data() {
		return {
			isHovered: false,

			highlightText: '',
			highlightOptions: {
				completeWords: false,
				ignoreCase: true,
			},
			
			highlightCount: 0,
			currentHighlightIndex: -1,
			totalMatches: [],

			pageToHighlight: null,
			pageToHighlightRefs: null,
			updateHighlight: 0,
		};
	},
	watch: {
		highlightText(newText, oldText) {
			if (newText !== oldText) {
				this.highlightPages = [];
				this.highlightCount = 0;
				this.totalMatches = [];
				this.currentHighlightIndex = -1;
			}
		}
	},
	computed: {
		highlightCountComputed() {
			return this.highlightPages.length;
		},
	},
	setup(props) {
		const { pdf, pages } = usePDF({ url: props.fileURL, verbosity: 0 });
		return { pdf, pages };
	},
	props: {
		id: {
			type: String,
			required: true
		},
		scale: {
			type: Number,
			default: 0.85
		},
		currentPage: {
			type: Number,
			required: true
		},
		fileURL: {
			type: [String, null],
			required: true
		},
		fileName: {
			type: String,
			required: true
		},
		isSearchInputVisible: {
			type: Boolean,
			required: false
		}
	},
	methods: {
		focusSearchInput() {
			const inputSearchElement = document.getElementById(`${this.id}-highlightText`);
			if (inputSearchElement) inputSearchElement.focus();
		},
		closeSearchInput() {
			this.$emit('close-search-input');
			this.highlightText = '';
		},
		scrollToPage(page, behavior = 'smooth') {
			const pageElement = this.$refs[`page-${page}`];
			if (pageElement && pageElement[0]) {
				pageElement[0].scrollIntoView({ behavior: behavior });
				this.$emit('page-changed', page);
			}
		},
		scrollToMatch(direction) {
			if (direction === 'next' && this.currentHighlightIndex < this.totalMatches.length - 1) {
				this.currentHighlightIndex++;
			} else if (direction === 'prev' && this.currentHighlightIndex > 0) {
				this.currentHighlightIndex--;
			}
			const match = this.totalMatches[this.currentHighlightIndex];
			if (match) {
				this.scrollToPage(match.page, 'auto');
			}
			this.applyCurrentHighlightClass(direction);
		},
		applyCurrentHighlightClass(direction) {
			if (direction === 'prev') this.updateHighlight--;

			// remove the class from all highlights
			document.querySelectorAll('.current-highlight').forEach(el => el.classList.remove('current-highlight'));

			const currentMatch = this.totalMatches[this.currentHighlightIndex];
			if (!currentMatch) return;

			if (!this.pageToHighlight || this.pageToHighlight !== currentMatch.page) {
				this.pageToHighlight = currentMatch.page;
				this.pageToHighlightRefs = this.$refs[`page-${currentMatch.page}`];
				this.updateHighlight = direction === 'prev' 
					? this.pageToHighlightRefs[0].querySelector('.textLayer').querySelectorAll('span.highlight').length 
					: 0;
			}

			if (!this.pageToHighlightRefs || !this.pageToHighlightRefs[0]) return;

			const textLayer = this.pageToHighlightRefs[0].querySelector('.textLayer');
			if (!textLayer) return;

			const spans = textLayer.querySelectorAll('span.highlight');

			spans.forEach((span, index) => {
				if (
					(direction === 'prev' && index === this.updateHighlight - 1) || 
					(direction === 'next' && index === this.updateHighlight)
				) {
					span.classList.add('current-highlight');
				} else {
					span.classList.remove('current-highlight');
				}
			});

			if (direction === 'next') this.updateHighlight++;
		},
		onHighlight(highlightData) {
			if (highlightData.matches.length) {
				const totalMatches = new Set(this.totalMatches.map(match => JSON.stringify(match)) || []);
				highlightData.matches.forEach(match => {
					totalMatches.add(JSON.stringify({ ...match, page: highlightData.page }));
				});
				this.totalMatches = Array.from(totalMatches).map(match => JSON.parse(match)); // Parse back to objects
				this.totalMatches.sort((a, b) => a.page - b.page); // Sort by page in ascending order
			}
			this.highlightCount = this.totalMatches.length;

			// Update currentHighlightIndex to the first match
			// if (this.totalMatches.length > 0) {
			//     this.currentHighlightIndex = 0;
			//     const match = this.totalMatches[this.currentHighlightIndex];
			//     if (match) {
			//         this.scrollToPage(match.page,'auto');
			//     }
			// }
		},
	},
	updated() {
		this.$emit('total-pages', this.pages);
	}
}
</script>

<style scoped>
:deep(canvas) {
	border-radius: 10px;
	box-shadow: 0 .5rem 1rem rgba(0,0,0,.15);
}

:deep(.current-highlight) {
	background-color: yellow !important;
}
</style>