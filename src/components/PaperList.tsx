import { Card, ListGroup, Badge } from 'react-bootstrap';

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

interface PaperListProps {
  papers: Paper[];
}

const PaperList: React.FC<PaperListProps> = ({ papers }) => {
  return (
    <ListGroup className="mt-4">
      {papers.map((paper) => (
        <ListGroup.Item key={paper.id} className="mb-3 p-0 border-0">
          <Card className="shadow-sm h-100">
            <Card.Body className="d-flex flex-column">
              <Card.Title className="text-primary mb-2">{paper.title}</Card.Title>
              <Card.Subtitle className="mb-3 text-muted small">
                {paper.authors.join(', ')} - {new Date(paper.published).toLocaleDateString()}
              </Card.Subtitle>
              <hr className="my-2" />

              <h6 className="mb-1"><Badge bg="success" className="me-2">Key Contribution</Badge></h6>
              <p className="mb-2">{paper.aiSummary.keyContribution}</p>

              <h6 className="mb-1"><Badge bg="info" className="me-2">Novelty</Badge></h6>
              <p className="mb-3">{paper.aiSummary.novelty}</p>

              <h6 className="mb-1"><Badge bg="secondary" className="me-2">AI Summary</Badge></h6>
              <p className="mb-3">{paper.aiSummary.summary}</p>

              <details className="mt-auto pt-2 border-top">
                <summary className="text-muted small">Original Abstract</summary>
                <p className="mt-2 text-muted small">{paper.summary}</p>
              </details>

              <Card.Link href={paper.link} target="_blank" rel="noopener noreferrer" className="btn btn-outline-primary btn-sm mt-3 align-self-start">
                Read on arXiv
              </Card.Link>
            </Card.Body>
          </Card>
        </ListGroup.Item>
      ))}
    </ListGroup>
  );
};

export default PaperList;
