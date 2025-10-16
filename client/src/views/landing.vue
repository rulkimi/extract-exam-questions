<template>
  <div class="antialiased">
    <!-- Header -->
    <header class="absolute top-0 left-0 right-0 z-10 p-4">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-2xl font-bold text-white">Exam Extractor</h1>
        <a href="#signin"
          class="hidden md:inline-block bg-white text-indigo-600 font-semibold px-5 py-2 rounded-lg shadow-md hover:bg-gray-100 transition-colors">
          Get Started
        </a>
      </div>
    </header>

    <!-- Hero Section -->
    <main class="relative">
      <section class="gradient-bg text-white pt-32 pb-20">
        <div class="container mx-auto px-6 text-center">
          <h2 class="text-4xl md:text-6xl font-extrabold leading-tight mb-4">
            Stop the Copy-Paste Grind.
          </h2>
          <p class="text-lg md:text-xl max-w-3xl mx-auto mb-8 text-indigo-100">
            Extract questions, diagrams, and tables from any exam PDF and convert them into a perfectly formatted,
            editable Word document in seconds.
          </p>
          <div class="flex justify-center">
            <button @click="handleGetStarted"
              class="cursor-pointer bg-white text-indigo-600 font-bold py-4 px-8 rounded-lg shadow-xl hover:bg-gray-100 transition-transform transform hover:scale-105">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                class="h-6 w-6 inline-block mr-2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="8.5" cy="7" r="4"></circle>
                <line x1="20" y1="8" x2="20" y2="14"></line>
                <line x1="17" y1="11" x2="23" y2="11"></line>
              </svg>
              Create Free Account
            </button>
          </div>
          <p class="mt-4 text-sm text-indigo-200">Sign up and get 3 free conversions.</p>
        </div>
      </section>

      <!-- Visual representation of the process -->
      <div class="relative -mt-10">
        <div class="container mx-auto px-6">
          <div class="bg-white rounded-xl shadow-2xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-around">
            <!-- Left Side: PDF -->
            <div class="w-full md:w-5/12 p-4">
              <h3 class="text-lg font-semibold text-center mb-2">Your PDF Exam Paper</h3>
              <div
                class="bg-gray-100 border-2 border-dashed rounded-lg p-4 h-64 flex flex-col justify-center items-center text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16" fill="none" viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="mt-2 text-sm font-medium">Scanned or Digital PDF</p>
              </div>
            </div>

            <!-- Arrow -->
            <div class="text-indigo-500 my-4 md:my-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 transform md:rotate-0 rotate-90" fill="none"
                viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </div>

            <!-- Right Side: DOCX -->
            <div class="w-full md:w-5/12 p-4">
              <h3 class="text-lg font-semibold text-center mb-2">Editable DOCX File</h3>
              <div
                class="bg-indigo-50 border-2 border-dashed border-indigo-200 rounded-lg p-4 h-64 flex flex-col justify-center items-center text-indigo-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16" fill="none" viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="mt-2 text-sm font-medium">Ready-to-Use Word Doc</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Problem Section -->
      <section class="py-20 bg-gray-50">
        <div class="container mx-auto px-6 text-center">
          <h2 class="text-3xl md:text-4xl font-bold mb-4">The Tedious Process Teachers Face</h2>
          <p class="text-lg text-gray-600 max-w-3xl mx-auto mb-12">
            Inspired by my mother, a physics teacher, this tool solves the headache of manually re-creating exam papers
            from PDFs.
          </p>
          <div class="grid md:grid-cols-3 gap-8">
            <div class="bg-white p-6 rounded-lg shadow-md">
              <h3 class="font-semibold text-xl mb-2">Manual Copy & Paste</h3>
              <p class="text-gray-600">Endless, error-prone retyping of questions from scanned documents or protected
                PDFs.</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-md">
              <h3 class="font-semibold text-xl mb-2">Lost Formatting</h3>
              <p class="text-gray-600">Diagrams, tables, and text layouts get jumbled, requiring hours of tedious
                reformatting.</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-md">
              <h3 class="font-semibold text-xl mb-2">Wasted Time</h3>
              <p class="text-gray-600">Precious time spent on document formatting instead of focusing on teaching and
                students.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Solution/Features Section -->
      <section class="py-20 bg-white">
        <div class="container mx-auto px-6">
          <div class="text-center mb-16">
            <h2 class="text-3xl md:text-4xl font-bold mb-4">Your Workflow, Automated</h2>
            <p class="text-lg text-gray-600 max-w-3xl mx-auto">
              Our tool does the heavy lifting, giving you back hours of your valuable time.
            </p>
          </div>
          <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <!-- Feature 1 -->
            <div class="feature-card bg-gray-50 p-6 rounded-lg shadow-sm transition-all">
              <h3 class="font-bold text-xl mb-3 text-indigo-600">Smart Extraction</h3>
              <p class="text-gray-600">Supports both rasterized (scanned) and text-based PDFs, accurately identifying
                distinct questions.</p>
            </div>
            <!-- Feature 2 -->
            <div class="feature-card bg-gray-50 p-6 rounded-lg shadow-sm transition-all">
              <h3 class="font-bold text-xl mb-3 text-indigo-600">Preserves Layouts</h3>
              <p class="text-gray-600">Tables, complex diagrams, and multi-column text layouts are preserved in the
                final document.</p>
            </div>
            <!-- Feature 3 -->
            <div class="feature-card bg-gray-50 p-6 rounded-lg shadow-sm transition-all">
              <h3 class="font-bold text-xl mb-3 text-indigo-600">Clean DOCX Output</h3>
              <p class="text-gray-600">Generates a clean, standardized, and fully editable Word document without weird
                formatting issues.</p>
            </div>
            <!-- Feature 4 -->
            <div class="feature-card bg-gray-50 p-6 rounded-lg shadow-sm transition-all">
              <h3 class="font-bold text-xl mb-3 text-indigo-600">100% Web-Based</h3>
              <p class="text-gray-600">No software to install. Access it from any device, anytime. Your files are
                processed securely.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA Section -->
      <section class="py-20 gradient-bg" id="get-started">
        <div class="container mx-auto px-6 text-center text-white">
          <h2 class="text-4xl font-bold mb-4">Ready to Reclaim Your Time?</h2>
          <p class="text-lg max-w-2xl mx-auto mb-8 text-indigo-100">
            Spend less time fighting with documents and more time inspiring students. Try Exam Extractor today.
          </p>
          <button @click="handleGetStarted"
            class="bg-white text-indigo-600 font-bold py-4 px-8 rounded-lg shadow-xl hover:bg-gray-100 transition-transform transform hover:scale-105">
            Convert Your First Exam for Free
          </button>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8">
      <div class="container mx-auto px-6 text-center">
        <p>&copy; {{ currentYear }} Exam Extractor. Built for educators, by someone who gets it. 🚀</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
// In a standard Vue setup, you would use a script setup block for your logic.
const currentYear = new Date().getFullYear();

const handleGetStarted = () => {
  // In a real app, this would use Vue Router to navigate to a /register page
  // or use a state management variable to open a registration modal.
  console.log('Redirecting to registration page...');
  alert('Create your account to get started!\n(In a real app, you would be redirected to a registration page.)');
};
</script>

<style scoped>
/* These styles will be scoped to this component only.
  Note: Tailwind CSS classes used in the template are global and would be
  configured in your project's main CSS file or tailwind.config.js.
  The external fonts would be linked in your main index.html file.
*/
body {
  font-family: 'Inter', sans-serif;
}

.gradient-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>
