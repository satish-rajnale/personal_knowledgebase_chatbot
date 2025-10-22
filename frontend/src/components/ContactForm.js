import React, { useState } from 'react';
import { authAPI } from '../services/api';
import { Mail, Send, Loader } from 'lucide-react';

const ContactForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      await authAPI.submitContactForm(formData);
      setSuccess(true);
      setFormData({ name: '', email: '', subject: '', message: '' });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit contact form');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center mb-8">
          <div className="bg-primary-100 p-3 rounded-full w-fit mx-auto mb-4">
            <Mail className="h-8 w-8 text-primary-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Contact Support
          </h2>
          <p className="text-gray-600">
            Have a question or need help? I'd love to hear from you.
          </p>
        </div>

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-5 h-5 bg-green-400 rounded-full flex items-center justify-center">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">
                  Message sent successfully!
                </p>
                <p className="text-sm text-green-700 mt-1">
                  We'll get back to you as soon as possible.
                </p>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-5 h-5 bg-red-400 rounded-full flex items-center justify-center">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-red-800">
                  Error sending message
                </p>
                <p className="text-sm text-red-700 mt-1">
                  {error}
                </p>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Name
              </label>
              <input
                type="text"
                id="name"
                name="name"
                required
                value={formData.name}
                onChange={handleChange}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                placeholder="Your name"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                placeholder="your.email@example.com"
              />
            </div>
          </div>

          <div>
            <label htmlFor="subject" className="block text-sm font-medium text-gray-700">
              Subject
            </label>
            <input
              type="text"
              id="subject"
              name="subject"
              required
              value={formData.subject}
              onChange={handleChange}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              placeholder="What's this about?"
            />
          </div>

          <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-700">
              Message
            </label>
            <textarea
              id="message"
              name="message"
              rows={6}
              required
              value={formData.message}
              onChange={handleChange}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              placeholder="Tell us more about your question or issue..."
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {loading ? (
                <Loader className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Send className="h-4 w-4 mr-2" />
              )}
              Send Message
            </button>
          </div>
        </form>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="text-center">
            <h3 className="text-sm font-medium text-gray-900 mb-2">
              Other ways to get help
            </h3>
            <div className="text-sm text-gray-600 space-y-1">
              <p>• Contact me on <a style={{color: 'blue'}} href="mailto:satishrajnale98@gmail.com">satishrajnale@gmail.com</a></p>
              <p>• Check my <a href="https://github.com/satish-rajnale" target='_blank' style={{color: 'blue'}}>GitHub</a> for updates</p>
              <p>• Follow me on <a style={{color: 'blue'}} href='https://www.linkedin.com/in/satish-rajnale-676a201b1' target='_blank'>LinkedIn</a> or on my <a href="https://satishrajnale.vercel.app/" target='_blank' style={{color: 'blue'}}>portfolio</a> for updates</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactForm; 