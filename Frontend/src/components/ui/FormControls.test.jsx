import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { FormSection, StringInput, TextAreaInput, StringListInput } from './FormControls';

describe('FormControls', () => {
  describe('StringInput', () => {
    it('should render with label and value', () => {
      render(<StringInput label="Test Label" value="Test Value" onChange={vi.fn()} />);
      
      expect(screen.getByLabelText('Test Label')).toBeInTheDocument();
      expect(screen.getByLabelText('Test Label')).toHaveValue('Test Value');
    });

    it('should call onChange when value changes', () => {
      const mockOnChange = vi.fn();
      render(<StringInput label="Test Label" value="" onChange={mockOnChange} />);
      
      const input = screen.getByLabelText('Test Label');
      fireEvent.change(input, { target: { value: 'New Value' } });
      
      expect(mockOnChange).toHaveBeenCalledWith('New Value');
    });
  });

  describe('TextAreaInput', () => {
    it('should render with label and value', () => {
      render(<TextAreaInput label="Test Label" value="Test Value" onChange={vi.fn()} />);
      
      expect(screen.getByLabelText('Test Label')).toBeInTheDocument();
      expect(screen.getByLabelText('Test Label')).toHaveValue('Test Value');
    });

    it('should call onChange when value changes', () => {
      const mockOnChange = vi.fn();
      render(<TextAreaInput label="Test Label" value="" onChange={mockOnChange} />);
      
      const textarea = screen.getByLabelText('Test Label');
      fireEvent.change(textarea, { target: { value: 'New Value' } });
      
      expect(mockOnChange).toHaveBeenCalledWith('New Value');
    });
  });

  describe('StringListInput', () => {
    it('should render with label and values', () => {
      const values = ['Item 1', 'Item 2'];
      render(<StringListInput label="Test Label" values={values} onChange={vi.fn()} />);
      
      expect(screen.getByText('Test Label')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Item 1')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Item 2')).toBeInTheDocument();
    });

    it('should call onChange when adding a new item', () => {
      const mockOnChange = vi.fn();
      const values = ['Item 1'];
      render(<StringListInput label="Test Label" values={values} onChange={mockOnChange} />);
      
      const addButton = screen.getByText('Add Item');
      fireEvent.click(addButton);
      
      expect(mockOnChange).toHaveBeenCalledWith(['Item 1', '']);
    });

    it('should call onChange when removing an item', () => {
      const mockOnChange = vi.fn();
      const values = ['Item 1', 'Item 2'];
      render(<StringListInput label="Test Label" values={values} onChange={mockOnChange} />);
      
      const removeButtons = screen.getAllByRole('button', { name: '' });
      fireEvent.click(removeButtons[0]); // Click the first remove button (X icon)
      
      expect(mockOnChange).toHaveBeenCalledWith(['Item 2']);
    });

    it('should call onChange when changing an item', () => {
      const mockOnChange = vi.fn();
      const values = ['Item 1'];
      render(<StringListInput label="Test Label" values={values} onChange={mockOnChange} />);
      
      const input = screen.getByDisplayValue('Item 1');
      fireEvent.change(input, { target: { value: 'Updated Item 1' } });
      
      expect(mockOnChange).toHaveBeenCalledWith(['Updated Item 1']);
    });
  });
});