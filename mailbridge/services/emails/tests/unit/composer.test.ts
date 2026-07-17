import { renderTemplate } from '../../src/composer'

describe('composer.renderTemplate', () => {
  it('substitutes variables in html and subject', () => {
    const { subject, html } = renderTemplate('<p>Hello {{name}}</p>', 'Hi {{name}}', { name: 'Alice' })
    expect(subject).toBe('Hi Alice')
    expect(html).toBe('<p>Hello Alice</p>')
  })

  it('renders empty string for missing variables', () => {
    const { html } = renderTemplate('<p>{{missing}}</p>', 'sub', {})
    expect(html).toBe('<p></p>')
  })

  it('handles nested variables', () => {
    const { html } = renderTemplate('<p>{{user.name}}</p>', 'sub', { user: { name: 'Bob' } })
    expect(html).toBe('<p>Bob</p>')
  })

  it('renders multiple variables', () => {
    const { html } = renderTemplate('{{a}} and {{b}}', 'sub', { a: 'foo', b: 'bar' })
    expect(html).toBe('foo and bar')
  })
})
