import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

const DOCS_DIR = path.join(process.cwd(), 'content/docs')

export interface DocMeta {
  slug: string[]
  title: string
  description?: string
  lastUpdated: string
  order?: number
}

export interface Doc extends DocMeta {
  content: string
}

export function getAllDocs(): DocMeta[] {
  const files = fs.readdirSync(DOCS_DIR).filter(f => f.endsWith('.mdx'))
  return files
    .map(file => {
      const raw = fs.readFileSync(path.join(DOCS_DIR, file), 'utf8')
      const { data } = matter(raw)
      return {
        slug: [file.replace('.mdx', '')],
        title: data.title ?? file,
        description: data.description,
        lastUpdated: data.lastUpdated ? String(data.lastUpdated) : '',
        order: data.order ?? 99
      }
    })
    .sort((a, b) => (a.order ?? 99) - (b.order ?? 99))
}

export function getDoc(slug: string[]): Doc | null {
  const filePath = path.join(DOCS_DIR, `${slug.join('/')}.mdx`)
  if (!fs.existsSync(filePath)) return null
  const raw = fs.readFileSync(filePath, 'utf8')
  const { data, content } = matter(raw)
  return {
    slug,
    title: data.title ?? '',
    description: data.description,
    lastUpdated: data.lastUpdated ? String(data.lastUpdated) : '',
    order: data.order,
    content
  }
}
