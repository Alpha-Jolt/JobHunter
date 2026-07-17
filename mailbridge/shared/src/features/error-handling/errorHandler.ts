import { Request, Response, NextFunction } from 'express'
import { AppError } from './errors'
import { logger } from '../logging'

export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  _next: NextFunction
): void {
  if (err instanceof AppError) {
    if (err.statusCode >= 500) {
      logger.error({ err, req_id: req.id }, err.message)
    }
    res.status(err.statusCode).json({
      success: false,
      error: { code: err.code, message: err.message }
    })
    return
  }

  logger.error({ err, req_id: req.id }, 'Unhandled error')
  res.status(500).json({
    success: false,
    error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred' }
  })
}
