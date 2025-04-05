import bcrypt from 'bcryptjs';


export async function hashPassword(password: string) {
    const hash = await bcrypt.hash(password, 12);
    return hash;
}


export async function compareHash(passwordHash: string, inputPassword: string) {
    return bcrypt.compare(inputPassword, passwordHash);
}
