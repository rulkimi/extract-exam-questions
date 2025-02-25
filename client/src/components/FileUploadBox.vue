<template>
	<div class="flex flex-col justify-center items-center">
		<div
			class="transition-all ease duration-300 p-3 rounded-lg"
			:class="active ? 'bg-primary bg-opacity-25' : 'bg-white'"
		>
			<div
				@dragenter.prevent="toggleActive"
				@dragleave.prevent="toggleActive"
				@dragover.prevent
				@drop.prevent="filesDropped"
				@change="selectedFiles"
				class="dropzone transition-all ease duration-300 rounded-lg mx-auto px-4 flex flex-col gap-3 items-center text-lg justify-center text-center"
				:class="[
					!verticalUI || areFilesSelected ? 'flex md:flex-row justify-between py-4' : 'py-5',
					error ? 'error' : '',
					loading ? 'disabled' : ''
				]"
			>
				<font-awesome-icon
					class="transition-all ease duration-300 upload-icon"
					:class="[
						mediumIcon || areFilesSelected || skipInitialUpload ? 'upload-icon-md' : 'upload-icon-lg',
						areFilesSelected || skipInitialUpload ? 'order-md-first' : '',
						active ? 'active' : '',
						error ? 'text-red-500 shake' : loading ? 'text-slate-500' : 'text-teal-500'
					]"
					:icon="['fas', 'cloud-arrow-up']"
				/>
				<div class="flex flex-col items-center gap-2 text-lg">
					<span class="font-bold" :class="{ 'text-slate-500': loading }">{{ allowMultiple ? 'Select files' : 'Select file' }} or drag and drop here</span>
					<span v-if="!error" class="text-slate-500">{{ description }}</span>
					<span v-if="error" class="text-red-500">{{ errorMessage }}</span>
				</div>
				<label
					class="px-3 py-2 rounded-lg border cursor-pointer"
					:class="[
						areFilesSelected || skipInitialUpload ? 'order-md-last' : '',
						error ? ' text-red-500 border-red-500 hover:text-white hover:bg-red-500' : 'text-teal-500 border-teal-500 hover:text-white hover:bg-teal-500',
						loading ? '!text-slate-500 !border-slate-500' : ''
					]"
					for="dropzoneFile"
				>
					{{ allowMultiple ? 'Select Files' : 'Select File' }}
				</label>
				<input class="hidden dropzoneFile" type="file" id="dropzoneFile" ref="dropzoneFile" :accept="accept" :multiple="allowMultiple" :disabled="loading" />
			</div>
			<div v-if="areFilesSelected || skipInitialUpload" class="mt-4 flex flex-col">
				<div v-if="areFilesSelected" class="mb-3 ">
					<span class="text-sm text-black/60 font-medium">Files added:</span>
					<ul class="list-none">
						<li v-for="(file, index) in files" :key="index" class="flex justify-between items-center mt-2">
							<div>
								<font-awesome-icon class="text-teal-500 mr-2" :icon="getFileIcon(file)" size="xl" />
								<span>{{ truncateString(file.name, 25, 4) }}</span>
								<span class="text-slate-500">&#x30FB;</span>
								<a :href="getFileURL(file)" :download="file.name" target="_blank" class="text-teal-500 no-underline cursor-pointer">Preview</a>
							</div>
							<div>
								<span class="text-slate-500">{{ formatFileSize(file.size) }}</span>
								<font-awesome-icon
									class="text-slate-500 ml-2 cursor-pointer hover:scale-110"
									:icon="['fas', 'times']"
									@click="removeFile(index)"
								/>
							</div>
						</li>
					</ul>
				</div>
				<div class="transition-all ease duration-300" :class="{ 'active' : active, 'mt-3': areFilesSelected }">
					<slot name="custom-element"></slot>
				</div>
				<div class="flex justify-end mt-4 gap-2" v-if="!noUploadButton || !noCancelButton">
					<div class="flex gap-2">
						<button
							v-if="!noCancelButton"
							class="px-3 py-2 rounded-lg border text-teal-500 border-teal-500 hover:text-white hover:bg-teal-500"
							@click="cancel"
						>
							{{ cancelButtonText }}
						</button>
						<button v-if="!noUploadButton"
							class="px-3 py-2 rounded-lg border cursor-pointer text-white bg-teal-500 flex items-center gap-2"
							:class="{ 'w-full': noCancelButton, 'opacity-50' : loading }"
							:disabled="loading || !areFilesSelected || disableUploadButton"
							@click="upload"
						>
							<Spinner v-if="loading" />
							<span>{{ uploadButtonText }}</span>
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>
<script>
import { formatFileSize, truncateString } from '@/utils';
import Spinner from '@/components/Spinner.vue';

export default {
	name: 'DropZone',
  components: {
    Spinner
  },
	data() {
		return {
			active: false,
			files: [],
			error: false,
			errorMessage: '',
		}
	},
	emits: ['upload-files', 'cancel', 'file-changes'],
	props: {
		loading: {
			type: Boolean,
			required: true,
		},
		description: {
			type: String,
		},
		accept: {
			type: String,
			default: '*/*',
		},
		maxSize: {
			type: Number,
			default: 0,
		},
		allowMultiple: {
			type: Boolean,
			default: false,
		},
		maxFiles: {
			type: Number,
			default: 5,
		},
		autoUpload: {
			type: Boolean,
			default: false,
		},
		skipInitialUpload: {
			type: Boolean,
			default: false
		},
		noCancelButton: {
			type: Boolean,
			default: false
		},
		uploadButtonText: {
			type: String,
			default: 'Upload'
		},
		cancelButtonText: {
			type: String,
			default: 'Cancel'
		},
		disableUploadButton: {
			type: Boolean,
			default: false,
		},
		noUploadButton: {
			type: Boolean,
			default: false
		},
		mediumIcon: {
			type: Boolean,
			default: false
		},
		verticalUI : {
			type: Boolean,
			default: false
		},
	},
	computed: {
		areFilesSelected() {
			return this.files.length > 0;
		}
	},
	methods: {
		formatFileSize,
		truncateString,
		cancel() {
			this.removeAllFiles();
			this.$emit('cancel');
		},
		getFileIcon(file) {
			const iconMap = {
				'wordprocessingml': ['fas', 'file-word'],
				'spreadsheetml': ['fas', 'file-excel'],
				'pdf': ['fas', 'file-pdf'],
				'video': ['fas', 'file-video'],
				'powerpoint': ['fas', 'file-powerpoint'],
				'image': ['fas', 'file-image'],
				'csv': ['fas', 'file-csv'],
				'audio': ['fas', 'file-audio'],
			};

			if (!file) return ['fas', 'file']; // default icon if no file is selected

			const fileType = file.type;
			for (const [key, icon] of Object.entries(iconMap)) {
				if (fileType.includes(key)) {
					return icon;
				}
			}

			return ['fas', 'file']; // default icon if no specific type is matched
		},
		getFileURL(file) {
			return file ? URL.createObjectURL(file) : null;
		},
		toggleActive() {
			this.active = !this.active;
		},
		filesDropped(event) {            
			this.toggleActive();
			if (this.handleUploadInProgress()) return;
		
			const droppedFiles = Array.from(event.dataTransfer.files);
			this.handleFiles(droppedFiles);
		},
		selectedFiles() {
			if (this.handleUploadInProgress()) return;
			
			const fileInput = this.$refs.dropzoneFile;
			if (fileInput.files.length === 0) return;
			const selectedFiles = Array.from(fileInput.files);
			this.handleFiles(selectedFiles);
			this.$emit('file-changes', this.allowMultiple ? this.files : this.files[0]);
		},
		upload() {
			this.$emit('upload-files', this.allowMultiple ? this.files : this.files[0]);
		},
		removeAllFiles() {
			if (this.handleUploadInProgress()) return;

			this.files.forEach(file => {
				URL.revokeObjectURL(this.getFileURL(file)); // Revoke the object URL to avoid memory leaks
			});
			this.files = [];
			this.$refs.dropzoneFile.value = '';
			this.error = false;
			this.errorMessage = '';
		},
		removeFile(index) {
			if (this.handleUploadInProgress()) return;

			const file = this.files[index];
			URL.revokeObjectURL(this.getFileURL(file)); // Revoke the object URL to avoid memory leaks
			this.files.splice(index, 1);
			if(!this.allowMultiple) this.$refs.dropzoneFile.value = '';
		},
		handleFiles(newFiles) {
			// check if multiple file upload is not allowed but multiple files are provided
			if (!this.allowMultiple && newFiles.length > 1) {
				this.error = true;
				this.errorMessage = 'Only a single file can be uploaded.';
				return false;
			}

			// check if the number of new files exceeds the maxFiles limit
			const potentialNewFilesCount = this.allowMultiple ? this.files.length + newFiles.length : newFiles.length;
			if (potentialNewFilesCount > this.maxFiles) {
				this.error = true;
				this.errorMessage = `You can only upload up to ${this.maxFiles} file${this.maxFiles > 1 ? 's' : ''}.`;
				return false;
			}

			const validatedFiles = newFiles.filter(file => this.validateFile(file));
			if (validatedFiles.length === 0) {
				this.error = true; // Error is already set by validateFile
				return false;
			}

			this.error = false;
			if (this.allowMultiple) {
				this.files = this.files.concat(validatedFiles);
			} else {
				this.files = validatedFiles.slice(0, 1);
			}

			if (this.autoUpload) {
				this.upload();
			}

			return true;
		},
		validateFile(file) {
			if (!this.isFileTypeAccepted(file)) {
				this.errorMessage = `Only ${this.accept.replace(/\./g, '').split(',').join(', ')} files are allowed`;
				return false;
			}
			if (!this.isFileSizeAccepted(file)) {
				this.errorMessage = `File size should not exceed ${this.maxSize} MB`;
				return false;
			}
			return true;
		},
		handleUploadInProgress() {
			if (this.loading) {
				this.error = true;
				this.errorMessage = `Please cancel to upload new file.`;
				setTimeout(() => {
					this.error = false;
					this.errorMessage = '';
				}, 2000);
				return true;
			}
			return false;
		},
		isFileSizeAccepted(file) {
			if (this.maxSize === 0) return true; 
			return file.size <= this.maxSize * 1024 * 1024;
		},
		isFileTypeAccepted(file) {
			if (this.accept === '*/*') {
				return true;
			}
			const fileType = file.name.split('.').pop().toLowerCase();
			const acceptedTypes = this.accept.split(',').map(type => type.trim().substring(1));
			return acceptedTypes.includes(fileType);
		},
	}
};
</script>

<style scoped>
.dropzone {
	border: 3px dashed rgba(56, 178, 172, 0.45); /* bg-teal-500 color with 0.45 opacity */
	width: 65vw;
	max-width: 700px;
}

.dropzone.error {
	border: 3px dashed rgba(239, 68, 68, 0.35); 
}

.dropzone.disabled {
	pointer-events: none;
	opacity: 0.5;
}

.transition {
	transition: .3s ease all;
}

.upload-icon-md {
	font-size: 4rem;
}
.upload-icon-md.active {
	font-size: 5rem;
}

.upload-icon-lg {
	font-size: 9rem;
}
.upload-icon-lg.active  {
	font-size: 10rem;
}

.order-md-first {
	order: -1; 
}

.order-md-last {
	order: 3;
}

.flex-md-grow-1 {
	flex-grow: 1;
}

.hover-enlarge:hover {
	transform: scale(1.1); /* Adjust the scale value as needed */
}

@keyframes shake {
	0% { transform: translateX(0); }
	33% { transform: translateX(-5px); }
	66% { transform: translateX(5px); }
	100% { transform: translateX(0); }
}

.shake {
	animation: shake 0.15s linear 3;
}
</style>