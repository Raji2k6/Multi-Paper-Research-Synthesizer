import ChatInput from '../components/ChatInput'
import ErrorMessage from '../components/ErrorMessage'
import LoadingSpinner from '../components/LoadingSpinner'
import SynthesisResult from '../components/SynthesisResult'

export default function MultiPaperSynthesis({ question, onQuestionChange, result, history = [], loading, error, onSelectHistory, onSubmit }) {
  return <>
    <div className="page-heading">
      <span className="eyebrow">Comparative analysis</span>
      <h1>Multi-Paper Synthesis</h1>
      <p>Compare findings across multiple research papers.</p>
    </div>
    <div className="synthesis-workspace">
      <section className="panel synthesis-prompt">
        <h2>What should we compare?</h2>
        <p className="panel-subtitle">Ask a focused question and the backend will retrieve evidence from multiple papers.</p>
        <label className="field-label" htmlFor="synthesis-question">Research comparison question</label>
        <ChatInput
          id="synthesis-question"
          value={question}
          onChange={onQuestionChange}
          onSubmit={onSubmit}
          disabled={loading}
          placeholder="Compare how the uploaded papers describe the Spiral Model..."
          buttonLabel="Analyze Papers"
        />
      </section>
      {loading && <section className="panel analysis-progress" aria-live="polite">
        <LoadingSpinner label="Analyzing evidence across papers..." />
        <p>Retrieving relevant passages and preparing a cited comparison. This can take up to a minute when hosted AI generation is enabled.</p>
      </section>}
      <ErrorMessage message={error} />
      {result
        ? <SynthesisResult result={result} />
        : !loading && <section className="panel synthesis-empty">
          <h2>Your comparison will appear here</h2>
          <p>Results include paper-wise evidence, shared findings, differences, possible contradictions, and cited sources.</p>
        </section>}
      {history.length > 0 && <section className="panel synthesis-history">
        <h2>Saved comparisons</h2>
        <div className="history-list">
          {history.map((item) => <button
            className={`history-item${result?.id === item.id ? ' active' : ''}`}
            key={item.id}
            type="button"
            onClick={() => onSelectHistory(item)}
          >
            <span>{item.question}</span>
            <small>{item.documents_analyzed} papers · {item.created_at ? new Date(item.created_at).toLocaleString() : 'Just now'}</small>
          </button>)}
        </div>
      </section>}
    </div>
  </>
}