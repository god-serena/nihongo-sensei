import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import DocumentManager from '@/components/DocumentManager.vue'

// ── Mock API ────────────────────────────────────────────────────────────────

const mockUploadDocument = vi.fn()

vi.mock('@/services/api', () => ({
  uploadDocument: (...args) => mockUploadDocument(...args),
}))

// ── Helpers ─────────────────────────────────────────────────────────────────

function mountComponent() {
  const pinia = createPinia()
  return mount(DocumentManager, {
    global: { plugins: [pinia] },
  })
}

function makeFile(name = 'test.txt') {
  return new File(['hello world'], name, { type: 'text/plain' })
}

// ── Tests ───────────────────────────────────────────────────────────────────

describe('DocumentManager.vue', () => {
  beforeEach(() => {
    mockUploadDocument.mockReset().mockResolvedValue({ id: 1, title: 'test.txt', chunk_count: 5 })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the drop zone with upload prompt', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('Drag & drop files here')
    expect(wrapper.text()).toContain('click to browse')
  })

  it('shows a hidden file input', () => {
    const wrapper = mountComponent()
    const input = wrapper.find('input[type="file"]')
    expect(input.exists()).toBe(true)
  })

  it('calls uploadDocument when a file is selected via click', async () => {
    mockUploadDocument.mockResolvedValue({ id: 1, title: 'test.txt', chunk_count: 5 })
    const wrapper = mountComponent()
    const file = makeFile()

    // Simulate clicking the drop zone which triggers the hidden input
    const input = wrapper.find('input[type="file"]')
    Object.defineProperty(input.element, 'files', { value: [file], writable: false, configurable: true })
    await input.trigger('change')

    expect(mockUploadDocument).toHaveBeenCalledWith(file)
  })

  it('shows upload progress while uploading', async () => {
    let resolveUpload
    mockUploadDocument.mockReturnValue(new Promise((resolve) => { resolveUpload = resolve }))
    const wrapper = mountComponent()
    const file = makeFile()

    const input = wrapper.find('input[type="file"]')
    Object.defineProperty(input.element, 'files', { value: [file], writable: false, configurable: true })
    await input.trigger('change')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Uploading document')
    resolveUpload({ id: 1, title: 'test.txt', chunk_count: 5 })
    await wrapper.vm.$nextTick()
  })

  it('renders uploaded documents with chunk count badges', async () => {
    mockUploadDocument.mockResolvedValue({ id: 1, title: 'lesson.md', chunk_count: 12 })
    const wrapper = mountComponent()
    const file = makeFile('lesson.md')

    const input = wrapper.find('input[type="file"]')
    Object.defineProperty(input.element, 'files', { value: [file], writable: false, configurable: true })
    await input.trigger('change')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('lesson.md')
    expect(wrapper.text()).toContain('12 chunks')
  })

  it('shows error feedback on upload failure', async () => {
    let rejectUpload
    const uploadPromise = new Promise((resolve, reject) => {
      rejectUpload = reject
    })
    mockUploadDocument.mockReturnValue(uploadPromise)
    const wrapper = mountComponent()
    const file = makeFile()

    const input = wrapper.find('input[type="file"]')
    Object.defineProperty(input.element, 'files', { value: [file], writable: false, configurable: true })
    await input.trigger('change')
    await wrapper.vm.$nextTick()

    // Still uploading before rejection
    expect(wrapper.text()).toContain('Uploading document')

    // Reject the deferred promise
    const networkErr = Object.assign(new Error('Network error'), { name: 'NetworkError' })
    rejectUpload(networkErr)
    await new Promise(r => setTimeout(r, 10))
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Network error')
  })

  it('toggles drag-over class on drag events', async () => {
    const wrapper = mountComponent()
    const dropZone = wrapper.find('[class*="border-dashed"]')

    await dropZone.trigger('dragover')
    expect(dropZone.classes('border-blue-500')).toBe(true)

    await dropZone.trigger('dragleave')
    expect(dropZone.classes('border-blue-500')).toBe(false)
  })

  function dropWrapper(wrapper) {
    return wrapper
  }
})
