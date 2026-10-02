import { BookOpenCheck, Sparkles } from 'lucide-react'

export default function BrandMark() {
  return <span className="brand-mark" aria-hidden="true">
    <BookOpenCheck />
    <Sparkles className="brand-sparkle" size={10} />
  </span>
}
