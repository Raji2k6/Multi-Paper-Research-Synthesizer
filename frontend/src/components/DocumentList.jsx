import EmptyState from './EmptyState'
import PaperCard from './PaperCard'

export default function DocumentList({ documents }) {
  if (!documents.length) return <EmptyState message="Uploaded papers will appear here during this session." />
  return <div>{documents.map((document) => <PaperCard document={document} key={`${document.document_id}-${document.filename}`} />)}</div>
}