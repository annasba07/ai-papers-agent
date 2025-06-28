'use client';
import PaperList from '@/components/PaperList';
import { Container, Row, Col, Form, Button, Modal, InputGroup } from 'react-bootstrap';
import { useState, useEffect } from 'react';

interface Paper {
  id: string;
  title: string;
  authors: string[];
  published: string;
  summary: string;
  aiSummary: {
    summary: string;
    keyContribution: string;
    novelty: string;
  };
  link: string;
}

export default function Home() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterDays, setFilterDays] = useState('7');
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showTrendModal, setShowTrendModal] = useState(false);
  const [trendAnalysis, setTrendAnalysis] = useState('');
  const [loadingTrends, setLoadingTrends] = useState(false);

  useEffect(() => {
    const fetchPapers = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams({
          days: filterDays,
          category: filterCategory,
          query: searchQuery,
        });
        const response = await fetch(`/api/papers?${params.toString()}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: Paper[] = await response.json();
        setPapers(data);
      } catch (error) {
        console.error("Failed to fetch papers:", error);
        setPapers([]); // Clear papers on error
      } finally {
        setLoading(false);
      }
    };

    const handler = setTimeout(() => {
      fetchPapers();
    }, 500); // Debounce search input

    return () => {
      clearTimeout(handler);
    };
  }, [filterDays, filterCategory, searchQuery]);

  const handleShowTrends = async () => {
    setLoadingTrends(true);
    setShowTrendModal(true);
    try {
      const response = await fetch(`/api/papers/trends?category=${filterCategory}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTrendAnalysis(data.trendAnalysis);
    } catch (error) {
      console.error("Failed to fetch trend analysis:", error);
      setTrendAnalysis('Could not load trend analysis.');
    } finally {
      setLoadingTrends(false);
    }
  };

  const saveToDigest = () => {
    const digestSettings = { filterCategory, searchQuery };
    localStorage.setItem('aiPaperDigestSettings', JSON.stringify(digestSettings));
    alert('Digest settings saved!');
  };

  const loadFromDigest = () => {
    const savedSettings = localStorage.getItem('aiPaperDigestSettings');
    if (savedSettings) {
      const { filterCategory, searchQuery } = JSON.parse(savedSettings);
      setFilterCategory(filterCategory);
      setSearchQuery(searchQuery);
    }
  };

  return (
    <Container>
      <h1 className="my-4 text-center">AI Paper Digest</h1>
      <Row className="mb-4">
        <Col md={12} className="mb-3">
          <InputGroup>
            <Form.Control
              placeholder="Search by keywords (e.g., 'diffusion models', 'reinforcement learning')"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <Button onClick={saveToDigest}>Save to Digest</Button>
            <Button onClick={loadFromDigest}>My Digest</Button>
          </InputGroup>
        </Col>
        <Col md={4}>
          <Form.Group controlId="filterDays">
            <Form.Label>Filter by Days:</Form.Label>
            <Form.Control as="select" value={filterDays} onChange={(e) => setFilterDays(e.target.value)}>
              <option value="1">Last 24 Hours</option>
              <option value="3">Last 3 Days</option>
              <option value="7">Last 7 Days</option>
            </Form.Control>
          </Form.Group>
        </Col>
        <Col md={4}>
          <Form.Group controlId="filterCategory">
            <Form.Label>Filter by Category:</Form.Label>
            <Form.Control as="select" value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)}>
              <option value="all">All Categories</option>
              <option value="cs.AI">Artificial Intelligence</option>
              <option value="cs.LG">Machine Learning</option>
              <option value="cs.CV">Computer Vision</option>
              <option value="cs.CL">Computation and Language</option>
            </Form.Control>
          </Form.Group>
        </Col>
        <Col md={4} className="d-flex align-items-end">
          <Button onClick={handleShowTrends} className="w-100">
            {loadingTrends ? 'Analyzing...' : 'Analyze Trends'}
          </Button>
        </Col>
      </Row>
      {loading ? (
        <p className="text-center">Loading papers...</p>
      ) : papers.length > 0 ? (
        <PaperList papers={papers} />
      ) : (
        <p className="text-center">No papers found for the selected criteria.</p>
      )}

      <Modal show={showTrendModal} onHide={() => setShowTrendModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Trend Analysis</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {loadingTrends ? (
            <p>Loading analysis...</p>
          ) : (
            <pre style={{ whiteSpace: 'pre-wrap' }}>{trendAnalysis}</pre>
          )}
        </Modal.Body>
      </Modal>
    </Container>
  );
}