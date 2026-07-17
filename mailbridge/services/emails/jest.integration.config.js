module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/integration/**/*.test.ts', '**/e2e/**/*.test.ts'],
  setupFiles: ['<rootDir>/tests/fixtures/setupEnv.ts'],
  globals: { 'ts-jest': { tsconfig: 'tsconfig.test.json' } },
  testTimeout: 30000
}
