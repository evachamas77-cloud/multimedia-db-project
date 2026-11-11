

import { useState } from 'react'


import {
  getFrames,
  getFrameImageUrl,
  uploadFrame,
  getOCR,
  detectObjects,
  getFrameAnalyses
} from './services/api'


import './App.css'


function App() {
  
const [conversations, setConversations] = useState([])

  const [frames, setFrames] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
const [selectedFile, setSelectedFile] = useState(null)
const [uploading, setUploading] = useState(false)
const [uploadMessage, setUploadMessage] = useState('')

const [selectedFrameId, setSelectedFrameId] = useState('')
const [ocrResult, setOcrResult] = useState(null)
const [detectionResult, setDetectionResult] = useState(null)
const [analyzing, setAnalyzing] = useState(false)
const [analysisError, setAnalysisError] = useState('')

const [analysisHistory, setAnalysisHistory] = useState([])
const [historyLoading, setHistoryLoading] = useState(false)
const [historyError, setHistoryError] = useState('')



async function handleUpload() {
  if (!selectedFile) {
    setUploadMessage('Please select an image first.')
    return
  }

  setUploading(true)
  setUploadMessage('')

  try {
    await uploadFrame(selectedFile)
    setUploadMessage('Image uploaded successfully!')
    setSelectedFile(null)
    await loadFrames()
  } catch (err) {
    setUploadMessage('Upload failed. Backend may not be running.')
    console.error(err)
  } finally {
    setUploading(false)
  }
}


  async function loadFrames() {
    setLoading(true)
    setError('')

    try {
   const data = await getFrames()
      setFrames(data)
    } catch (err) {
      setError('Cannot connect to the backend server yet.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  
async function loadAnalysisHistory() {
  if (!selectedFrameId) {
    setHistoryError('Please select a frame first.')
    return
  }

  setHistoryLoading(true)
  setHistoryError('')
  setAnalysisHistory([])

  try {
    const data = await getFrameAnalyses(selectedFrameId)
   setAnalysisHistory(data.analyses ?? [])
  } catch (err) {
    setHistoryError('Cannot load analysis history. Backend may not be running.')
    console.error(err)
  } finally {
    setHistoryLoading(false)
  }
}

  
async function handleOCR() {
  if (!selectedFrameId) {
    setAnalysisError('Please select a frame first.')
    return
  }

  setAnalyzing(true)
  setAnalysisError('')
  setOcrResult(null)

  try {
    const result = await getOCR(selectedFrameId)
    setOcrResult(result)
  } catch (err) {
    setAnalysisError('OCR failed. Backend may not be running.')
    console.error(err)
  } finally {
    setAnalyzing(false)
  }
}

async function handleDetection() {
  if (!selectedFrameId) {
    setAnalysisError('Please select a frame first.')
    return
  }

  setAnalyzing(true)
  setAnalysisError('')
  setDetectionResult(null)

  try {
    const result = await detectObjects(selectedFrameId)
    setDetectionResult(result)
  } catch (err) {
    setAnalysisError('Object detection failed. Backend may not be running.')
    console.error(err)
  } finally {
    setAnalyzing(false)
  }
}


  return (

    <main className="dashboard">
      <header className="dashboard-header">
        <h1>Multimedia Database Dashboard</h1>
        <p>AI Assistant for Visually Impaired People</p>
      </header>

      <section className="dashboard-grid">
        <div className="dashboard-card">
          <h2>📱 Live Phone Camera</h2>
          <p>Waiting for Android phone connection...</p>
          <div className="video-placeholder">
            Live video will appear here
          </div>
        </div>

       
<div className="dashboard-card">
  <h2>🖼️ Stored Frames</h2>

  
<div className="upload-section">
  <h3>Upload an Image</h3>

  <input
    type="file"
    accept="image/*"
    onChange={(e) => {
      setSelectedFile(e.target.files[0] || null)
      setUploadMessage('')
    }}
  />

  <button
    type="button"
    onClick={handleUpload}
    disabled={uploading || !selectedFile}
  >
    {uploading ? 'Uploading...' : 'Upload Image'}
  </button>

  {uploadMessage && <p role="status">{uploadMessage}</p>}
</div>


  <button type="button" onClick={loadFrames} disabled={loading}>
    {loading ? 'Loading...' : 'Refresh Frames'}
  </button>

  {error && <p role="alert">{error}</p>}

  {!loading && !error && frames.length === 0 && (
    <p>No stored frames loaded yet.</p>
  )}

  
<div className="frames-gallery">
  {frames.map((frame) => (
    <div key={frame.id} className="frame-item">
      <img
        src={getFrameImageUrl(frame.id)}
        alt={`Stored frame ${frame.id}`}
      />

      <p>Frame #{frame.id}</p>

      <p>
        {frame.uploaded_at
          ? new Date(frame.uploaded_at).toLocaleString()
          : 'Date unavailable'}
      </p>

      <button
        type="button"
        onClick={() => {
          setSelectedFrameId(String(frame.id))
          setOcrResult(null)
          setDetectionResult(null)
          setAnalysisError('')
        }}
      >
        Select for Analysis
      </button>
    </div>
  ))}
</div>

</div>


        
<div className="dashboard-card">
  <h2>🔍 OCR & Object Detection</h2>

  <p>Select a stored frame to analyze.</p>

  <select
    value={selectedFrameId}
    onChange={(e) => {
      setSelectedFrameId(e.target.value)
      setOcrResult(null)
      setDetectionResult(null)
      setAnalysisError('')
    }}
  >
    <option value="">Choose a frame</option>

    {frames.map((frame) => (
      <option key={frame.id} value={frame.id}>
        Frame #{frame.id}
      </option>
    ))}
  </select>


<div className="analysis-buttons">
  <button
    type="button"
    onClick={handleOCR}
    disabled={analyzing || !selectedFrameId}
  >
    Run OCR
  </button>

  <button
    type="button"
    onClick={handleDetection}
    disabled={analyzing || !selectedFrameId}
  >
    Detect Objects
  </button>

  <button
    type="button"
    onClick={loadAnalysisHistory}
    disabled={historyLoading || !selectedFrameId}
  >
    {historyLoading
      ? 'Loading History...'
      : 'View Analysis History'}
  </button>
</div>


{historyError && (
  <p role="alert">{historyError}</p>
)}

{analysisHistory.length > 0 && (
  <div className="analysis-result">
    <h3>Previous Analyses</h3>

    {analysisHistory.map((analysis) => (
      <div key={analysis.analysis_id}>
        <h4>{analysis.analysis_type}</h4>

        <p>
          {analysis.created_at
            ? new Date(analysis.created_at).toLocaleString()
            : 'Date unavailable'}
        </p>

        <pre>
          {JSON.stringify(analysis.results, null, 2)}
        </pre>
      </div>
    ))}
  </div>
)}


  {analyzing && <p role="status">Analyzing image...</p>}

  {analysisError && (
    <p role="alert">{analysisError}</p>
  )}

  {ocrResult && (
    <div className="analysis-result">
      <h3>OCR Results</h3>
      <pre>{JSON.stringify(ocrResult, null, 2)}</pre>
    </div>
  )}

  {detectionResult && (
    <div className="analysis-result">
      <h3>Object Detection Results</h3>
      <pre>{JSON.stringify(detectionResult, null, 2)}</pre>
    </div>
  )}
</div>


        
<div className="dashboard-card">
  <h2>🎤 Questions & Answers</h2>

  <p>
    Voice questions and AI-generated answers
    will appear here.
  </p>

 
<div className="qa-section">
  <h3>Conversation History</h3>

  {conversations.length === 0 ? (
    <p className="qa-empty">
      No questions or answers available yet.
    </p>
  ) : (
    <div className="conversation-list">
      {conversations.map((conversation, index) => (
        <div
          className="conversation-item"
          key={conversation.id ?? index}
        >
          <p>
            <strong>Question:</strong> {conversation.question}
          </p>

          <p>
            <strong>AI Answer:</strong> {conversation.answer}
          </p>

          {conversation.created_at && (
            <small>
              {new Date(
                conversation.created_at
              ).toLocaleString()}
            </small>
          )}
        </div>
      ))}
    </div>
  )}
</div>

</div>

      </section>
    </main>
  )
}

export default App
