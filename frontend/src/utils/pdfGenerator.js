import { jsPDF } from "jspdf";

export const generatePDF = (markdownText, companyName, roleName) => {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });

  const pageHeight = doc.internal.pageSize.height;
  const pageWidth = doc.internal.pageSize.width;
  const margin = 20;
  const contentWidth = pageWidth - (margin * 2);
  
  let y = 30; // Start position below header

  const drawHeaderAndFooter = (pageNum) => {
    // Header
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.setTextColor(100, 116, 139); // slate-500
    doc.text(`PlacementPrep AI | Preparation Report`, margin, 12);
    doc.text(`${companyName} - ${roleName}`, pageWidth - margin, 12, { align: 'right' });
    
    // Draw line below header
    doc.setDrawColor(203, 213, 225); // slate-300
    doc.setLineWidth(0.2);
    doc.line(margin, 14, pageWidth - margin, 14);

    // Footer
    doc.setDrawColor(203, 213, 225);
    doc.setLineWidth(0.2);
    doc.line(margin, pageHeight - 15, pageWidth - margin, pageHeight - 15);
    
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.setTextColor(100, 116, 139);
    doc.text(`Confidential - For Personal Preparation Only`, margin, pageHeight - 10);
    doc.text(`Page ${pageNum}`, pageWidth - margin, pageHeight - 10, { align: 'right' });
  };

  // Split markdown into lines
  const lines = markdownText.split('\n');
  let pageNum = 1;
  drawHeaderAndFooter(pageNum);

  // Set default text styling
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(30, 41, 59); // slate-800

  const checkPageBreak = (neededHeight) => {
    if (y + neededHeight > pageHeight - 20) {
      doc.addPage();
      pageNum += 1;
      y = 30;
      drawHeaderAndFooter(pageNum);
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line === '') {
      y += 4;
      continue;
    }

    // Headers
    if (line.startsWith('# ')) {
      const headingText = line.substring(2).replace(/\*\*/g, '');
      checkPageBreak(15);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(18);
      doc.setTextColor(15, 23, 42); // slate-900
      y += 4;
      doc.text(headingText, margin, y);
      y += 8;
      // Reset
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(30, 41, 59);
    } 
    else if (line.startsWith('## ')) {
      const headingText = line.substring(3).replace(/\*\*/g, '');
      checkPageBreak(12);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(14);
      doc.setTextColor(15, 23, 42);
      y += 4;
      doc.text(headingText, margin, y);
      y += 6;
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(30, 41, 59);
    }
    else if (line.startsWith('### ')) {
      const headingText = line.substring(4).replace(/\*\*/g, '');
      checkPageBreak(10);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(11);
      doc.setTextColor(15, 23, 42);
      y += 3;
      doc.text(headingText, margin, y);
      y += 5;
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(30, 41, 59);
    }
    // Blockquotes
    else if (line.startsWith('>')) {
      const quoteText = line.replace(/^>\s*/, '').replace(/\*\*/g, '');
      const splitQuote = doc.splitTextToSize(quoteText, contentWidth - 8);
      const boxHeight = (splitQuote.length * 5) + 6;
      checkPageBreak(boxHeight + 4);
      
      // Draw light gray box with left blue accent line
      doc.setFillColor(248, 250, 252); // slate-50
      doc.rect(margin, y, contentWidth, boxHeight, "F");
      doc.setFillColor(59, 130, 246); // blue-500
      doc.rect(margin, y, 1.5, boxHeight, "F");
      
      doc.setFont("helvetica", "oblique");
      doc.setFontSize(9.5);
      doc.setTextColor(71, 85, 105); // slate-600
      
      for (let j = 0; j < splitQuote.length; j++) {
        doc.text(splitQuote[j], margin + 5, y + 5 + (j * 5));
      }
      y += boxHeight + 4;
      
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(30, 41, 59);
    }
    // Lists
    else if (line.startsWith('* ') || line.startsWith('- ')) {
      const listText = line.substring(2).replace(/\*\*/g, '');
      const splitText = doc.splitTextToSize(listText, contentWidth - 8);
      checkPageBreak((splitText.length * 5) + 2);
      
      doc.setFont("helvetica", "normal");
      doc.setTextColor(30, 41, 59);
      doc.text("•", margin + 2, y + 1);
      for (let j = 0; j < splitText.length; j++) {
        doc.text(splitText[j], margin + 6, y + 1 + (j * 5));
      }
      y += (splitText.length * 5) + 1;
    }
    // Numbered Lists
    else if (/^\d+\.\s+/.test(line)) {
      const match = line.match(/^(\d+\.)\s+/);
      const prefix = match[1];
      const listText = line.substring(match[0].length).replace(/\*\*/g, '');
      const splitText = doc.splitTextToSize(listText, contentWidth - 8);
      checkPageBreak((splitText.length * 5) + 2);
      
      doc.setFont("helvetica", "bold");
      doc.text(prefix, margin + 1, y + 1);
      doc.setFont("helvetica", "normal");
      for (let j = 0; j < splitText.length; j++) {
        doc.text(splitText[j], margin + 8, y + 1 + (j * 5));
      }
      y += (splitText.length * 5) + 1;
    }
    // Normal Text / Paragraphs
    else {
      const cleanLine = line.replace(/\*\*/g, '');
      const splitText = doc.splitTextToSize(cleanLine, contentWidth);
      checkPageBreak((splitText.length * 5) + 2);
      
      doc.setFont("helvetica", "normal");
      doc.setTextColor(30, 41, 59);
      for (let j = 0; j < splitText.length; j++) {
        doc.text(splitText[j], margin, y + 1 + (j * 5));
      }
      y += (splitText.length * 5) + 2;
    }
  }

  doc.save(`${companyName.toLowerCase().replace(/\s+/g, '_')}_prep_report.pdf`);
};
