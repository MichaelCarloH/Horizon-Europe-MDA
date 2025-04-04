import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Hero from '../app/components/hero';
import LessonsInfo from '@/app/components/lessons_info';
import PGInfo from '@/app/components/chatbot_info';
import Home from '@/app/page';

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

describe('Home Page', () => {
    test('renders all components correctly', () => {
        render(<Home />);
        
        // Check if Hero, PGInfo, and LessonsInfo components are rendered
        expect(screen.getByText(/Your gateway to understanding neural networks/i)).toBeInTheDocument();
        expect(screen.getByText(/Learning Rate is an educational website designed to teach/i)).toBeInTheDocument();
        expect(screen.getByText(/Implement with the Playground/i)).toBeInTheDocument();
        expect(screen.getByText(/The playground is an interactive platform/i)).toBeInTheDocument();
        expect(screen.getByText(/Learn with Interactive Lessons/i)).toBeInTheDocument();
        expect(screen.getByText(/Embark on an interactive journey through the intricacies of neural networks/i)).toBeInTheDocument();
    });

    test('elements become visible based on IntersectionObserver', () => {
        render(<Home />);

        // Check if elements within each child component become visible after IntersectionObserver triggers
        // For Hero component
        expect(screen.getByText(/Your gateway to understanding neural networks/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByText(/Learning Rate is an educational website designed to teach/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByRole('button', { name: /more info/i })).toBeVisible();

        // For PGInfo component
        expect(screen.getByText(/Implement with the Playground/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByText(/The playground is an interactive platform/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByRole('button', { name: /go to playground/i })).toBeVisible();

        // For LessonsInfo component
        expect(screen.getByText(/Learn with Interactive Lessons/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByText(/Embark on an interactive journey through the intricacies of neural networks/i).parentElement).toHaveClass('opacity-100');
        expect(screen.getByRole('button', { name: /go to lessons/i })).toBeVisible();
    });
});