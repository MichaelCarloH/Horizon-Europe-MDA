import { PrismaClient } from '@prisma/client'
import { mockDeep, mockReset, DeepMockProxy } from 'jest-mock-extended'
import '@testing-library/jest-dom';

import client from '@/data/prisma'

jest.mock('./prisma', () => ({
  __esModule: true,
  default: mockDeep<PrismaClient>(),
}))

beforeEach(() => {
  mockReset(prismaMock)
})

export const prismaMock = client as unknown as DeepMockProxy<PrismaClient>