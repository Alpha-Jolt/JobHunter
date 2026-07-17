import Handlebars from 'handlebars'

export function renderTemplate(
  templateHtml: string,
  subject: string,
  variables: Record<string, unknown>
): { subject: string; html: string } {
  const compiledHtml = Handlebars.compile(templateHtml)
  const compiledSubject = Handlebars.compile(subject)
  return {
    subject: compiledSubject(variables),
    html: compiledHtml(variables)
  }
}
