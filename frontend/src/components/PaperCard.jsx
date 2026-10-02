import { FileText, Trash2 } from 'lucide-react'

export default function PaperCard({ document, onDelete }) {
  return <article className="file-row"><FileText size={20} /><div><strong>{document.title || document.filename}</strong><span>{document.filename} · {document.chunk_count} searchable chunks</span></div><button className="icon-button" type="button" aria-label={`Delete ${document.title || document.filename}`} onClick={() => onDelete(document.document_id)}><Trash2 size={16} /></button></article>
}