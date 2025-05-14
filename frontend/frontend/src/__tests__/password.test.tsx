import bcrypt from 'bcryptjs'; // Still import bcrypt
import {hashPassword, compareHash} from '../utils/password'
jest.mock('bcryptjs'); // Mock bcrypt for testing purposes (optional)


// Your tests:

describe('Password Utility Functions', () => {
  test('hashPassword should call bcrypt.hash with the correct arguments', async () => {
    const password = 'secret123';
    await hashPassword(password);

    // Assert that bcrypt.hash was called with the expected arguments
    expect(bcrypt.hash).toHaveBeenCalledWith(password, 12);
  });

  test('compareHash should call bcrypt.compare with the correct arguments', async () => {
    const passwordHash = 'hashedPassword';
    const inputPassword = 'secret123';
    await compareHash(passwordHash, inputPassword);

    // Assert that bcrypt.compare was called with the expected arguments
    expect(bcrypt.compare).toHaveBeenCalledWith(inputPassword, passwordHash);
  });

  // Test return values based on your implementation logic
});
