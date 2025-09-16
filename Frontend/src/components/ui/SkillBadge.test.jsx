import { render, screen } from '@testing-library/react';
import SkillBadge from './SkillBadge';

describe('SkillBadge', () => {
  it('should render with present type', () => {
    render(<SkillBadge text="Python" type="present" />);
    const badge = screen.getByText('Python');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-green-100', 'text-green-700');
  });

  it('should render with absent type', () => {
    render(<SkillBadge text="Java" type="absent" />);
    const badge = screen.getByText('Java');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-red-100', 'text-red-700');
  });

  it('should render with partial type', () => {
    render(<SkillBadge text="JavaScript" type="partial" />);
    const badge = screen.getByText('JavaScript');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-yellow-100', 'text-yellow-700');
  });
});