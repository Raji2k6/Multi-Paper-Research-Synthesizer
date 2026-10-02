import { FileUp, UploadCloud } from 'lucide-react'
import { useRef, useState } from 'react'
import { uploadDocument } from '../api/uploadApi'
import { getFriendlyError } from '../api/errors'
import ErrorMessage from './ErrorMessage'
import LoadingSpinner from './LoadingSpinner'

export default function FileUpload({ onUploaded }) {
  const inputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const selectFile = (candidate) => { if (!candidate || !candidate.name.toLowerCase().endsWith('.pdf')) { setError('Please choose a PDF file.'); setFile(null); return } setFile(candidate); setError(''); setSuccess('') }
  const submit = async () => { if (!file) return; setLoading(true); setError(''); setSuccess(''); try { await uploadDocument(file); await onUploaded(); setSuccess('Paper uploaded and ingestion completed successfully.'); setFile(null); if (inputRef.current) inputRef.current.value = '' } catch (requestError) { setError(getFriendlyError(requestError)) } finally { setLoading(false) } }
  return <div><div className={`upload-zone${dragging ? ' dragging' : ''}`} onDragOver={(event) => { event.preventDefault(); setDragging(true) }} onDragLeave={() => setDragging(false)} onDrop={(event) => { event.preventDefault(); setDragging(false); selectFile(event.dataTransfer.files[0]) }}><UploadCloud size={32} color="#236b58" /><h3>{file ? file.name : 'Drop your PDF here'}</h3><p>{file ? 'Ready to process this research paper.' : 'or choose a PDF from your device'}</p><input ref={inputRef} className="file-input" type="file" accept="application/pdf" onChange={(event) => selectFile(event.target.files[0])} /><button className="button secondary" onClick={() => inputRef.current?.click()}><FileUp size={15} /> Choose PDF</button></div><ErrorMessage message={error} />{success && <div className="success">{success}</div>}<button className="button full" disabled={!file || loading} onClick={submit}>{loading ? <LoadingSpinner label="Processing paper..." /> : 'Upload research paper'}</button></div>
}