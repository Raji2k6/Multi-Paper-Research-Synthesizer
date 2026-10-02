import ChatInput from '../components/ChatInput'
import ChatMessage from '../components/ChatMessage'
import EmptyState from '../components/EmptyState'
import ErrorMessage from '../components/ErrorMessage'
import LoadingSpinner from '../components/LoadingSpinner'

export default function ResearchChat({ question, onQuestionChange, messages, loading, error, onSubmit }) { return <><div className="page-heading"><span className="eyebrow">Grounded conversation</span><h1>Research Assistant</h1><p>Ask questions about your uploaded research papers.</p></div><section className="panel chat-panel"><ErrorMessage message={error} />{messages.length ? <div className="message-list">{messages.map((message, index) => <ChatMessage message={message} key={index} />)}{loading && <div className="message ai"><LoadingSpinner label="Researching..." /></div>}</div> : <EmptyState message="Your research conversation will appear here. Start with a question about the papers you uploaded." />}<ChatInput value={question} onChange={onQuestionChange} onSubmit={onSubmit} disabled={loading} placeholder="Ask a question about your papers..." /></section></> }