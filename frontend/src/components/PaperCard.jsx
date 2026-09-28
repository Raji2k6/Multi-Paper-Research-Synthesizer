import { FileText } from 'lucide-react'

export default function PaperCard({ document }) {
  return <article className="file-row"><FileText size={20} /><div><strong>{document.title || document.filename}</strong><span>{document.filename} · Document ID: {document.document_id}</span></div></article>
}