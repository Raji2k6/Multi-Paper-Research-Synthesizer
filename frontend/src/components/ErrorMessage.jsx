import { AlertCircle } from 'lucide-react'

export default function ErrorMessage({ message }) { return message ? <div className="alert"><AlertCircle size={15} /> {message}</div> : null }