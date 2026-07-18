export class AppError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly statusCode: number = 500
  ) {
    super(message)
    this.name = 'AppError'
  }
}

export class ValidationError extends AppError {
  constructor(message: string, code = 'VALIDATION_ERROR') {
    super(code, message, 400)
    this.name = 'ValidationError'
  }
}

export class AuthenticationError extends AppError {
  constructor(message: string, code = 'AUTHENTICATION_ERROR') {
    super(code, message, 401)
    this.name = 'AuthenticationError'
  }
}

export class AuthorizationError extends AppError {
  constructor(message: string, code = 'AUTHORIZATION_ERROR') {
    super(code, message, 403)
    this.name = 'AuthorizationError'
  }
}

export class NotFoundError extends AppError {
  constructor(message: string, code = 'NOT_FOUND') {
    super(code, message, 404)
    this.name = 'NotFoundError'
  }
}

export class ConflictError extends AppError {
  constructor(message: string, code = 'CONFLICT') {
    super(code, message, 409)
    this.name = 'ConflictError'
  }
}

export class ExternalServiceError extends AppError {
  constructor(message: string, code = 'EXTERNAL_SERVICE_ERROR') {
    super(code, message, 502)
    this.name = 'ExternalServiceError'
  }
}

export class InternalError extends AppError {
  constructor(message: string, code = 'INTERNAL_ERROR') {
    super(code, message, 500)
    this.name = 'InternalError'
  }
}
