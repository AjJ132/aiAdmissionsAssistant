import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ContactUsButton } from '../ContactUsButton';

describe('ContactUsButton', () => {
  it('should render the Contact Us button', () => {
    render(<ContactUsButton />);
    
    const button = screen.getByRole('button', { name: /contact graduate admissions/i });
    expect(button).toBeInTheDocument();
    expect(screen.getByText('Contact Us')).toBeInTheDocument();
  });

  it('should toggle contact info on button click', () => {
    render(<ContactUsButton />);
    
    // Initially, contact info should not be visible
    expect(screen.queryByText('Graduate Admissions')).not.toBeInTheDocument();
    
    // Click the button to show contacts
    const button = screen.getByRole('button', { name: /contact graduate admissions/i });
    fireEvent.click(button);
    
    // Now contact info should be visible
    expect(screen.getByText('Graduate Admissions')).toBeInTheDocument();
    expect(screen.getByText('graduate@kennesaw.edu')).toBeInTheDocument();
    expect(screen.getByText('470-578-4377')).toBeInTheDocument();
  });

  it('should show email and phone links when expanded', () => {
    render(<ContactUsButton />);
    
    // Click to expand
    fireEvent.click(screen.getByRole('button', { name: /contact graduate admissions/i }));
    
    // Check for email link
    const emailLink = screen.getByRole('link', { name: /email graduate@kennesaw.edu/i });
    expect(emailLink).toHaveAttribute('href', 'mailto:graduate@kennesaw.edu');
    
    // Check for phone link
    const phoneLink = screen.getByRole('link', { name: /phone 470-578-4377/i });
    expect(phoneLink).toHaveAttribute('href', 'tel:470-578-4377');
  });

  it('should close contact info when close button is clicked', () => {
    render(<ContactUsButton />);
    
    // Click to expand
    fireEvent.click(screen.getByRole('button', { name: /contact graduate admissions/i }));
    expect(screen.getByText('Graduate Admissions')).toBeInTheDocument();
    
    // Click the close button
    const closeButton = screen.getByRole('button', { name: /close contact info/i });
    fireEvent.click(closeButton);
    
    // Contact info should be hidden
    expect(screen.queryByText('Graduate Admissions')).not.toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(<ContactUsButton className="custom-class" />);
    
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
