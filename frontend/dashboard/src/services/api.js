
const API_BASE_URL = 'http://127.0.0.1:8000'

// Check if the backend is running
export async function checkBackendStatus() {
  const response = await fetch(`${API_BASE_URL}/`)

  if (!response.ok) {
    throw new Error('Backend connection failed')
  }

  return response.json()
}

// Retrieve all stored frames
export async function getFrames() {
  const response = await fetch(`${API_BASE_URL}/frames`)

  if (!response.ok) {
    throw new Error('Failed to retrieve frames')
  }

  return response.json()
}

// Get the URL of a stored image
export function getFrameImageUrl(frameId) {
  return `${API_BASE_URL}/frames/${frameId}/image`
}

// Upload an image to the backend
export async function uploadFrame(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/upload-frame`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error('Image upload failed')
  }

  return response.json()
}

// Retrieve OCR results
export async function getOCR(frameId, language = 'en') {
  const response = await fetch(
    `${API_BASE_URL}/frames/${frameId}/ocr?language=${encodeURIComponent(language)}`
  )

  if (!response.ok) {
    throw new Error('OCR request failed')
  }

  return response.json()
}

// Retrieve object detection results
export async function detectObjects(frameId) {
  const response = await fetch(
    `${API_BASE_URL}/frames/${frameId}/detect`
  )

  if (!response.ok) {
    throw new Error('Object detection request failed')
  }

  return response.json()
}

// Retrieve saved analyses for a frame
export async function getFrameAnalyses(frameId) {
  const response = await fetch(
    `${API_BASE_URL}/frames/${frameId}/analyses`
  )

  if (!response.ok) {
    throw new Error('Failed to retrieve analyses')
  }

  return response.json()
}


export function getDetectedImageUrl(frameId) {
  return `${API_BASE_URL}/frames/${frameId}/detected-image`
}

export async function analyzeFrameQuality(frameId) {
  const response = await fetch(
    `${API_BASE_URL}/frames/${frameId}/analyze`
  )

  if (!response.ok) {
    throw new Error('Image quality analysis failed')
  }

  return response.json()
}

