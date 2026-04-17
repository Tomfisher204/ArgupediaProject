import '@testing-library/jest-dom';

// suppress noisy jsdom network errors
const originalError = console.error;

beforeAll(() => {
  jest.spyOn(console, 'error').mockImplementation((...args) => {
    const msg = args[0]?.toString?.() || '';

    if (
      msg.includes('AggregateError') ||
      msg.includes('XMLHttpRequest') ||
      msg.includes('Network request failed')
    ) {
      return;
    }

    originalError(...args);
  });

  // ALSO suppress fetch-level unhandled rejections
  const originalUnhandled = process.listeners('unhandledRejection')[0];
  process.removeAllListeners('unhandledRejection');

  process.on('unhandledRejection', (err) => {
    if (
      err?.name === 'AggregateError' ||
      err?.message?.includes('fetch') ||
      err?.message?.includes('Network request failed')
    ) {
      return;
    }
    originalUnhandled?.(err);
  });
});