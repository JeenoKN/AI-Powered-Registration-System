import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Locate directory-view-container
start_idx = text.find('<!-- FORM DIRECTORY — Glassmorphism Reskin -->')
end_idx = text.find('<div class="dashboard-view-container" v-show="currentTab === \'dashboard\'">')

if start_idx == -1 or end_idx == -1:
    print("Could not find directory section boundaries.")
    exit(1)

new_directory_section = '''<!-- FORM DIRECTORY — Tailwind Reskin -->
      <div class="directory-view-container min-h-screen bg-gray-50/30" v-show="currentTab === 'directory'">

        <!-- Page Header -->
        <div class="px-8 pt-8">
          <div class="flex justify-between items-start flex-wrap gap-4 mb-2">
            <div>
              <h1 class="text-3xl font-extrabold tracking-tight text-gray-900 mb-1">Form Directory</h1>
              <p class="text-sm text-gray-500">Manage and organize all your AI-generated forms.</p>
            </div>
            
            <!-- Search Bar -->
            <div class="flex items-center bg-white rounded-full px-5 py-2.5 border border-gray-200 shadow-sm gap-2 min-w-[260px] focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-500 transition-all">
              <svg class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
              <input type="text" v-model="searchQuery" placeholder="Search forms..." class="bg-transparent border-none outline-none text-sm text-gray-900 w-full placeholder-gray-400" />
            </div>
          </div>
          
          <div class="flex items-center gap-2 mt-6 mb-8">
            <button class="px-4 py-1.5 bg-gray-900 text-white rounded-full text-xs font-semibold shadow-sm hover:bg-gray-800 transition-colors">All Forms</button>
            <span class="text-xs text-gray-500 font-medium ml-2">{{ filteredDirectoryForms.length }} forms</span>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loadingDirectory" class="flex items-center justify-center py-20 gap-3 text-gray-500">
          <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          Loading forms...
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredDirectoryForms.length === 0" class="flex flex-col items-center justify-center py-20 gap-4 text-center">
          <div class="w-16 h-16 bg-indigo-50 rounded-2xl flex items-center justify-center">
            <svg class="w-8 h-8 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
          </div>
          <p class="text-gray-500 text-sm">No forms found. Create your first form!</p>
        </div>

        <!-- Component Grid -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 px-8 pb-8">
          <FormCard 
            v-for="form in filteredDirectoryForms" 
            :key="form.id" 
            :form="form" 
            @view="openViewModal" 
            @duplicate="duplicateForm" 
            @delete="deleteSavedForm" 
          />
        </div>
      </div>

      '''

text = text[:start_idx] + new_directory_section + text[end_idx:]

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Directory section replaced with Tailwind & Component structure!")
