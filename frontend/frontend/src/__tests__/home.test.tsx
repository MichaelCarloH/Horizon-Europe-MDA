import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Hero from '../app/components/hero';
import LessonsInfo from '@/app/components/lessons_info';
import PGInfo from '@/app/components/chatbot_info';


// Mock next/image to avoid fetchPriority warning
jest.mock('next/image', () => {
    const MockedImage = ({ src, alt, ...props }: { src: string, alt: string, props: any }) => (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={src} alt={alt} {...props} />
    );
    MockedImage.displayName = 'NextImageMock';
    return MockedImage;
});

// Mock IntersectionObserver
class MockIntersectionObserver implements IntersectionObserver {
    constructor(callback: IntersectionObserverCallback, options?: IntersectionObserverInit) {
        this.callback = callback;
        this.options = options;
    }

    root: Element | Document | null = null;
    rootMargin: string = '';
    thresholds: ReadonlyArray<number> = [];
    callback: IntersectionObserverCallback;
    options?: IntersectionObserverInit;

    observe(target: Element) {
        this.callback([{ isIntersecting: true, target }] as IntersectionObserverEntry[], this);
    }

    unobserve() {
        return null;
    }

    disconnect() {
        return null;
    }

    takeRecords(): IntersectionObserverEntry[] {
        return [];
    }
}

global.IntersectionObserver = MockIntersectionObserver;

describe('Hero Component', () => {
    test('renders Hero component correctly', () => {
        render(<Hero />);
        
        // Check if header, paragraph, button, and image elements are in the document
        expect(screen.getByText(/Your gateway to understanding neural networks/i)).toBeInTheDocument();
        expect(screen.getByText(/Learning Rate is an educational website designed to teach/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /more info/i })).toBeInTheDocument();
        expect(screen.getByAltText(/hero/i)).toBeInTheDocument();
    });

    test('elements become visible based on IntersectionObserver', () => {
        render(<Hero />);

        // Check if header, paragraph, button, and image elements are visible
        expect(screen.getByText(/Your gateway to understanding neural networks/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByText(/Learning Rate is an educational website designed to teach/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByRole('button', { name: /more info/i })!.parentElement!.parentElement).toHaveClass('opacity-100');
        expect(screen.getByAltText(/hero/i).parentElement).toHaveClass('opacity-100');
    });
});

describe('LessonsInfo Component', () => {
    test('renders LessonsInfo component correctly', () => {
        render(<LessonsInfo />);
        
        // Check if header, paragraph, images, and button elements are rendered
        expect(screen.getByText(/Learn with Interactive Lessons/i)).toBeInTheDocument();
        expect(screen.getByText(/Embark on an interactive journey through the intricacies of neural networks/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /go to lessons/i })).toBeInTheDocument();
        expect(screen.getAllByAltText(/content/i)).toHaveLength(3); // Use getAllByAltText for multiple images
    });

    test('elements become visible based on IntersectionObserver', () => {
        render(<LessonsInfo />);

        // Check if elements become visible after IntersectionObserver triggers
        expect(screen.getByText(/Learn with Interactive Lessons/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByText(/Embark on an interactive journey through the intricacies of neural networks/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByRole('button', { name: /go to lessons/i })).toBeVisible(); // Check if button is visible
        expect(screen.getAllByAltText(/content/i)[0].parentElement).toBeVisible();
    });
});

describe('PGInfo Component', () => {
    test('renders PGInfo component correctly', () => {
        render(<PGInfo />);
        
        // Check if header, paragraph, image, and button elements are rendered
        expect(screen.getByText(/Implement with the Playground/i)).toBeInTheDocument();
        expect(screen.getByText(/The playground is an interactive platform/i)).toBeInTheDocument();
        expect(screen.getByAltText(/hero/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /go to playground/i })).toBeInTheDocument();
    });

    test('elements become visible based on IntersectionObserver', () => {
        render(<PGInfo />);

        // Check if elements become visible after IntersectionObserver triggers
        expect(screen.getByText(/Implement with the Playground/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByText(/The playground is an interactive platform/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByAltText(/hero/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByRole('button', { name: /go to playground/i })).toBeVisible();
    });
});

