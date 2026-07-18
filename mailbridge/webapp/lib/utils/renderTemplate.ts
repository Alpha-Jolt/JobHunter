// Browser-safe Handlebars-compatible preview renderer.
// Supports {{var}}, {{#if key}}...{{/if}}, {{#each arr}}...{{/each}}
export function renderTemplate(template: string, context: Record<string, unknown>): string {
  let out = template
  out = out.replace(/\{\{#each (\w+)\}\}([\s\S]*?)\{\{\/each\}\}/g, (_, key, body) => {
    const arr = context[key]
    if (!Array.isArray(arr)) return ''
    return arr.map(item => body.replace(/\{\{this\}\}/g, String(item))).join('')
  })
  out = out.replace(/\{\{#if (\w+)\}\}([\s\S]*?)\{\{\/if\}\}/g, (_, key, body) => {
    return context[key] ? body : ''
  })
  out = out.replace(/\{\{(\w+)\}\}/g, (_, key) => {
    const val = context[key]
    return val !== undefined ? String(val) : `{{${key}}}`
  })
  return out
}
