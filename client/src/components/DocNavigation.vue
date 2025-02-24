<template>
	<div class="w-full bg-gray-100 shadow-sm rounded-md p-1 flex flex-col gap-2">
		<transition name="appear">
			<span v-if="pageInputError" class="w-full flex text-red-500 justify-center">Page doesn't exist</span>
		</transition>
		<div class="flex items-center gap-2">
			<div class="flex items-center gap-2">
				<div class="flex gap-1">
					<button class="px-2 py-1 rounded bg-gray-300" type="button" @click="previousPage">
						<font-awesome-icon :icon="['fas', 'chevron-left']" size="sm" />
					</button>
					<input
						:id="id + 'page-number'"
						type="number"
						class="w-[40px] border outline-none text-center bg-gray-300"
						:class="{ 'border-red-500 border-2': pageInputError }"
						:value="currentPage"
						@change="handlePageInput($event)"
						min="1"
						:max="totalPages"
					/>
					<button class="px-2 py-1 rounded bg-gray-300" type="button" @click="nextPage">
						<font-awesome-icon :icon="['fas', 'chevron-right']" size="sm" />
					</button>
				</div>
				<span class="whitespace-nowrap">of {{ totalPages }}</span>
			</div>
			<div class="flex border-l border-gray-500">
				<button class="p-1 ml-1" @click="zoomIn">
					<font-awesome-icon :icon="['fas', 'plus']" size="sm" />
				</button>
				<button class="p-1" @click="zoomOut">
					<font-awesome-icon :icon="['fas', 'minus']" size="sm" />
				</button>
			</div>
			<div class="flex border-l border-gray-500">
				<button class="p-1 mx-1" @click="search">
					<font-awesome-icon :icon="['fas', 'search']" size="sm" />
				</button>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	emits: [
		'next-page',
		'previous-page',
		'zoom-in',
		'zoom-out',
		'page-changed',
		'search-text'
	],
	props: {
		id: {
			type: String,
			required: true
		},
		totalPages: {
			type: Number,
			required: true
		},
		currentPage: {
			type: Number,
			required: true
		}
	},
	data() {
		return {
			pageInputError: false
		};
	},
	methods: {
		handlePageInput(event) {
			const page = parseInt(event.target.value);
			if (page >= 1 && page <= this.totalPages) {
				this.pageInputError = false;
				this.$emit('page-changed', page);
			} else {
				this.pageInputError = true;
				setTimeout(() => {
					this.pageInputError = false;
				}, 1000);
			}
		},
		nextPage() {
			this.pageInputError = false;
			if (this.currentPage >= this.totalPages) return;
			this.$emit('next-page', this.currentPage + 1);
		},
		previousPage() {
			this.pageInputError = false;
			if (this.currentPage <= 1) return;
			this.$emit('previous-page', this.currentPage - 1);
		},
		zoomIn() {
			this.$emit('zoom-in');
		},
		zoomOut() {
			this.$emit('zoom-out');
		},
		search() {
			this.$emit('search-text');
		}
	}
}
</script>

<style scoped>
/* Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
	-webkit-appearance: none;
	margin: 0;
}

input[type=number] {
	-moz-appearance: textfield; /* Firefox */
	appearance: textfield; /* Standard property for compatibility */
}

.appear-enter-active, .appear-leave-active {
	transition: all 0.3s ease;
}

.appear-leave-to, .appear-enter-from {
	opacity: 0;
	transform: translateY(20px);
}
</style>