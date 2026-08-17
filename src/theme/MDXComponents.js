import MDXComponents from '@theme-original/MDXComponents';
import Quiz from '@site/src/components/Quiz';
import Exercise, {Solution} from '@site/src/components/Exercise';
import TradeExample from '@site/src/components/TradeExample';
import Checklist from '@site/src/components/Checklist';
import Figure from '@site/src/components/Figure';

// Composants disponibles dans tous les fichiers Markdown sans import.
export default {
  ...MDXComponents,
  Quiz,
  Exercise,
  Solution,
  TradeExample,
  Checklist,
  Figure,
};
