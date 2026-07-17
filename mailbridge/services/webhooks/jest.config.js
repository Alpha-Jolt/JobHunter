module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/unit/**/*.test.ts'],
  setupFiles: ['<rootDir>/tests/fixtures/setupEnv.ts'],
  globals: { 'ts-jest': { tsconfig: 'tsconfig.test.json' } },
  passWithNoTests: false,
  coverageThreshold: { global: { lines: 80, functions: 80, branches: 80 } }
}
