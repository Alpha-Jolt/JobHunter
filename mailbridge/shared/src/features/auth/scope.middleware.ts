import { Request, Response, NextFunction } from 'express'
import { AuthorizationError } from '../error-handling'

export function requireScope(scope: string) {
  return (req: Request, _res: Response, next: NextFunction): void => {
    // JWT users: full access (scopes not applicable)
    if (!req.apiKeyScopes) return next()
    
    if (!req.apiKeyScopes.includes(scope)) {
      return next(new AuthorizationError(`API key missing scope: ${scope}`, 'INSUFFICIENT_SCOPE'))
    }
    
    next()
  }
}
