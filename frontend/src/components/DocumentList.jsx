import EmptyState from './EmptyState'
import PaperCard from './PaperCard'
import { deleteDocument } from '../api/documentsApi'
import { getFriendlyError } from '../api/errors'
import { useState } from 'react'
import ErrorMessage from './ErrorMessage'

export default function DocumentList({ documents, onDeleted }) {
  const [error, setError] = useState('')
  const removeDocument = async (documentId) => {
    try {
      await deleteDocument(documentId)
      await onDeleted()
      setError('')
    } catch (requestError) {
      setError(getFriendlyError(requestError))
    }
  }

  if (!documents.length) return <><ErrorMessage message={error} /><EmptyState message="Uploaded papers will appear here after they are added to the research library." /></>
  return <div><ErrorMessage message={error} />{documents.map((document) => <PaperCard document={document} onDelete={removeDocument} key={document.document_id} />)}</div>
}