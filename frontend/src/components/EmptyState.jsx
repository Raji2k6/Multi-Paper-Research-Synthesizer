import { Inbox } from 'lucide-react'

export default function EmptyState({ message }) { return <div className="empty-state"><Inbox size={28} /><p>{message}</p></div> }