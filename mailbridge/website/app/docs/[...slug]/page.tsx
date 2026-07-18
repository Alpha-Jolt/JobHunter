import { notFound } from 'next/navigation'
import { MDXRemote } from 'next-mdx-remote/rsc'
import { getDoc, getAllDocs } from '@/lib/docs'
import type { Metadata } from 'next'
import remarkGfm from 'remark-gfm'
import rehypeSlug from 'rehype-slug'
import rehypeHighlight from 'rehype-highlight'

interface Props {
  params: Promise<{ slug: string[] }>
}

export async function generateStaticParams() {
  return getAllDocs().map(d => ({ slug: d.slug }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const doc = getDoc(slug)
  return { title: doc?.title ?? 'Docs' }
}

export default async function DocPage({ params }: Props) {
  const { slug } = await params
  const doc = getDoc(slug)
  if (!doc) notFound()

  return (
    <article>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[var(--text)] mb-2">{doc.title}</h1>
        {doc.description && <p className="text-[var(--text-muted)]">{doc.description}</p>}
        {doc.lastUpdated && (
          <p className="mt-3 text-xs text-[var(--text-muted)]">Last updated: {doc.lastUpdated}</p>
        )}
      </div>
      <div className="prose prose-sm max-w-none">
        <MDXRemote
          source={doc.content}
          options={{
            mdxOptions: {
              remarkPlugins: [remarkGfm],
              rehypePlugins: [rehypeSlug, rehypeHighlight]
            }
          }}
        />
      </div>
    </article>
  )
}
