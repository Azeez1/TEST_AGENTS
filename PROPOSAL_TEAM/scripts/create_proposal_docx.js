const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        TableOfContents, PageBreak, ShadingType, LevelFormat, PageNumber } = require('docx');
const fs = require('fs');

// Create the proposal document matching Dux Machina EISM style - FLOWING PROSE (no PESTO labels)
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } }, // 11pt default
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 120, after: 120 }, outlineLevel: 2 } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    properties: {
      page: { margin: { top: 720, right: 720, bottom: 720, left: 720 } } // 0.5 inch margins
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun("Page "), new TextRun({ children: [PageNumber.CURRENT] }), new TextRun(" of "), new TextRun({ children: [PageNumber.TOTAL_PAGES] })]
      })] })
    },
    children: [
      // ============ COVER PAGE ============
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600 }, children: [] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "EDUCATION & TRAINING OFFICE", bold: true, size: 56, font: "Arial" })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "TECHNOLOGY SUPPORT SERVICES", bold: true, size: 56, font: "Arial" })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [
        new TextRun({ text: "Proposal Response Document", size: 28, font: "Arial" })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400 }, children: [] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "Solicitation Number: FA560625Q2038", size: 22 })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "Contracting Agency: 52D Contracting Squadron, USAFE", size: 22 })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "Location: Spangdahlem Air Base, Germany", size: 22 })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "NAICS Code: 541519 - Other Computer Related Services", size: 22 })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "Submission Deadline: 12 January 2026, 1600 CEST", size: 22 })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600 }, children: [
        new TextRun({ text: "SUBMITTED BY", bold: true, size: 24 })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "[COMPANY NAME]", bold: true, size: 32 })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "[Company Tagline]", size: 22 })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [
        new TextRun({ text: "Submission Date: [DATE]", size: 22 })
      ]}),

      // Page break after cover
      new Paragraph({ children: [new PageBreak()] }),

      // ============ TABLE OF CONTENTS ============
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Table of Contents")] }),
      new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
      new Paragraph({ children: [new PageBreak()] }),

      // ============ VOLUME 1: EXPERIENCE EXHIBIT ============
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Volume 1: Experience Exhibit")] }),

      // Section 1.1 - FLOWING PROSE (no PESTO labels)
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 Company Qualifications Overview")] }),
      new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Requirement: ", italics: true }), new TextRun("Describe in detail how the Offeror demonstrates the required experience per SOL M.1 and PWS Section 2 qualification requirements.")] }),
      new Paragraph({ children: [] }),
      // Flowing paragraph combining all PESTO elements
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] brings over [X] years of comprehensive IT support experience to the 52nd Fighter Wing Education & Training Office. Our team has consistently delivered mission-critical technology services across DoD installations, with specific expertise in the hybrid Windows/Linux/Apple environments that characterize modern Air Force education facilities. "),
        new TextRun({ text: "Per SOL M.1 evaluation criteria", bold: true }),
        new TextRun(", our personnel each possess a minimum of five years of demonstrated experience in hardware/software support, enterprise WI-FI management, cross-platform system administration, and DoD information security compliance. This depth of experience enables us to provide the Education Office with qualified technicians who can immediately contribute to mission success without extensive onboarding or training delays.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Our approach to IT support integrates industry-standard methodologies with DoD-specific requirements, leveraging tools such as Microsoft System Center for infrastructure monitoring, Ubiquiti UniFi Controller for enterprise WI-FI management, and Jamf Pro for Apple device administration. This comprehensive toolset, combined with our Security+ certified workforce, ensures we can maintain the zero-defect performance standards specified in "),
        new TextRun({ text: "PWS Section 7 Service Summary", bold: true }),
        new TextRun(" while reducing operational risk and maximizing system availability for Education Office personnel.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 1.2 - Personnel Qualifications
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.2 Personnel Qualifications")] }),
      new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Requirement: ", italics: true }), new TextRun("Provide key personnel resume(s) demonstrating 5+ years experience in each required skill area per PWS Section 2.")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Key Personnel - IT Support Specialist", bold: true, underline: {} })] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Name: ", bold: true }), new TextRun("[CANDIDATE NAME]")] }),
      new Paragraph({ children: [new TextRun({ text: "Years of Experience: ", bold: true }), new TextRun("[X] years in IT support services")] }),
      new Paragraph({ children: [new TextRun({ text: "Security Clearance: ", bold: true }), new TextRun("[SECRET/TOP SECRET] (SF-86 adjudicated)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Hardware/Software Support (5+ years): ", bold: true }), new TextRun("[Describe specific experience with computers, servers, peripherals, troubleshooting. Include DoD contract names and dates.]")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Enterprise WI-FI Management (5+ years): ", bold: true }), new TextRun("[Describe Ubiquiti/Cisco/enterprise WI-FI deployment and management experience. Include scale - number of access points, users supported.]")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Windows Administration (5+ years):", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Windows Server 2016/2019/2022 administration")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Windows 11 endpoint management")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Active Directory management")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Group Policy configuration")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Microsoft Hyper-V virtualization")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Linux Administration (5+ years):", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Ubuntu Server administration")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("CentOS/RHEL management")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Linux-based digital signage systems")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Bash scripting and automation")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Apple Administration (5+ years):", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("macOS Server configuration")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("iPad/iPod MDM management via Jamf")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Apple deployment programs (DEP/VPP)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("iOS troubleshooting and support")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "DoD/AF Information Security (5+ years):", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("DOD 5200.1-R compliance implementation")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("AFI 31-401 security awareness training")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("NIST 800-171 control implementation")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("DFARS 252.204-7012 cyber incident procedures")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Security Awareness training delivery")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Certifications:", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("CompTIA Security+ CE")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("CompTIA Network+")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("CompTIA A+")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Microsoft Certified: Azure Administrator")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Ubiquiti Enterprise Wireless Admin (UEWA)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Apple Certified Support Professional (ACSP)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Per PWS Section 2", bold: true }),
        new TextRun(", this candidate demonstrates the required minimum 5 years of experience in each mandated skill area, ensuring the Education & Training Office receives qualified support from day one of contract performance.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 1.3 Past Performance
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.3 Past Performance References")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] provides three references demonstrating our capability to perform IT support services of similar scope, scale, and complexity. "),
        new TextRun({ text: "Per SOL M.1", bold: true }),
        new TextRun(", each reference includes contract details, performance outcomes, and direct contact information for verification.")
      ]}),
      new Paragraph({ children: [] }),

      // Reference 1
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Reference 1: [CONTRACT NAME]")] }),
      new Paragraph({ children: [new TextRun({ text: "Contract Number: ", bold: true }), new TextRun("[Contract Number]")] }),
      new Paragraph({ children: [new TextRun({ text: "Agency/Client: ", bold: true }), new TextRun("[Agency Name]")] }),
      new Paragraph({ children: [new TextRun({ text: "Contract Value: ", bold: true }), new TextRun("$[Value]")] }),
      new Paragraph({ children: [new TextRun({ text: "Period of Performance: ", bold: true }), new TextRun("[Start Date] - [End Date]")] }),
      new Paragraph({ children: [new TextRun({ text: "Point of Contact: ", bold: true }), new TextRun("[Name], [Title]")] }),
      new Paragraph({ children: [new TextRun({ text: "Phone: ", bold: true }), new TextRun("[Phone Number]")] }),
      new Paragraph({ children: [new TextRun({ text: "Email: ", bold: true }), new TextRun("[Email Address]")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Scope of Work: ", bold: true }), new TextRun("[Describe IT support services provided - should mirror the Education Office requirements]")] }),
      new Paragraph({ children: [new TextRun({ text: "Scale: ", bold: true }), new TextRun("[X] users supported, [X] servers managed, [X] workstations maintained")] }),
      new Paragraph({ children: [new TextRun({ text: "Outcomes: ", bold: true }), new TextRun("[99.X%] system availability, [X]-hour average response time, Zero security incidents")] }),
      new Paragraph({ children: [] }),

      // Reference 2
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Reference 2: [CONTRACT NAME]")] }),
      new Paragraph({ children: [new TextRun({ text: "Contract Number: ", bold: true }), new TextRun("[Contract Number]")] }),
      new Paragraph({ children: [new TextRun({ text: "Agency/Client: ", bold: true }), new TextRun("[Agency Name]")] }),
      new Paragraph({ children: [new TextRun({ text: "Contract Value: ", bold: true }), new TextRun("$[Value]")] }),
      new Paragraph({ children: [new TextRun({ text: "Period of Performance: ", bold: true }), new TextRun("[Start Date] - [End Date]")] }),
      new Paragraph({ children: [new TextRun({ text: "Point of Contact: ", bold: true }), new TextRun("[Name], [Title]")] }),
      new Paragraph({ children: [new TextRun({ text: "Phone: ", bold: true }), new TextRun("[Phone Number]")] }),
      new Paragraph({ children: [new TextRun({ text: "Email: ", bold: true }), new TextRun("[Email Address]")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Scope of Work: ", bold: true }), new TextRun("[Describe IT support services provided]")] }),
      new Paragraph({ children: [new TextRun({ text: "Scale: ", bold: true }), new TextRun("[X] users supported, [X] servers managed")] }),
      new Paragraph({ children: [new TextRun({ text: "Outcomes: ", bold: true }), new TextRun("[List measurable outcomes]")] }),
      new Paragraph({ children: [] }),

      // Reference 3
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Reference 3: [CONTRACT NAME]")] }),
      new Paragraph({ children: [new TextRun({ text: "Contract Number: ", bold: true }), new TextRun("[Contract Number]")] }),
      new Paragraph({ children: [new TextRun({ text: "Agency/Client: ", bold: true }), new TextRun("[Agency Name]")] }),
      new Paragraph({ children: [new TextRun({ text: "Contract Value: ", bold: true }), new TextRun("$[Value]")] }),
      new Paragraph({ children: [new TextRun({ text: "Period of Performance: ", bold: true }), new TextRun("[Start Date] - [End Date]")] }),
      new Paragraph({ children: [new TextRun({ text: "Point of Contact: ", bold: true }), new TextRun("[Name], [Title]")] }),
      new Paragraph({ children: [new TextRun({ text: "Phone: ", bold: true }), new TextRun("[Phone Number]")] }),
      new Paragraph({ children: [new TextRun({ text: "Email: ", bold: true }), new TextRun("[Email Address]")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Scope of Work: ", bold: true }), new TextRun("[Describe IT support services provided]")] }),
      new Paragraph({ children: [new TextRun({ text: "Scale: ", bold: true }), new TextRun("[X] users supported, [X] servers managed")] }),
      new Paragraph({ children: [new TextRun({ text: "Outcomes: ", bold: true }), new TextRun("[List measurable outcomes]")] }),
      new Paragraph({ children: [new PageBreak()] }),

      // ============ VOLUME 2: TECHNICAL EXHIBIT ============
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Volume 2: Technical Exhibit")] }),

      // Section 2.1 - FLOWING PROSE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Technical Approach Overview")] }),
      new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Requirement: ", italics: true }), new TextRun("Describe in detail how the Offeror's solution addresses all technical requirements per PWS Section 10 specific tasks.")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] delivers a comprehensive IT support solution specifically designed to meet the Education & Training Office's mission requirements at Spangdahlem Air Base. Our technical approach addresses "),
        new TextRun({ text: "all 14 specific tasks outlined in PWS Section 10", bold: true }),
        new TextRun(" through a combination of proactive maintenance, rapid incident response, and continuous security monitoring. By maintaining qualified personnel on-site during duty hours and establishing robust on-call procedures, we ensure the Education Office maintains maximum system availability while meeting the zero-defect performance standards specified in the Service Summary.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Our execution methodology employs a structured service delivery framework that integrates ticketing, documentation, and continuous improvement. Using ServiceNow for incident management, Microsoft Intune and Jamf Pro for endpoint management, and Ubiquiti UniFi Controller for network administration, we maintain complete visibility into system health and can rapidly address issues before they impact mission operations. "),
        new TextRun({ text: "Per PWS Section 7 SS-1 through SS-4", bold: true }),
        new TextRun(", this approach ensures we consistently meet or exceed the performance standards of 0-2 defects per month across all service areas.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.2 - System Administration - FLOWING PROSE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 System Administration (PWS 10a)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] provides comprehensive system administration services for all computers, servers, and peripheral equipment supporting the Education & Training Office. "),
        new TextRun({ text: "Per PWS Section 10a", bold: true }),
        new TextRun(", our technicians perform daily monitoring, maintenance, and troubleshooting to ensure maximum system availability. Our administration methodology follows ITIL best practices adapted for DoD environments, with each morning beginning with a structured health check of all systems, reviewing event logs, verifying backup completion, and addressing any overnight alerts.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("For the specific technology stack at the Education Office, we employ Windows Server 2016 and SBS 2011 administration (Active Directory management, Group Policy maintenance, print server administration, file share management), Windows 11 endpoint management (security configuration, software deployment, patch management via WSUS/Intune), and peripheral equipment support (printers, scanners, display devices). Using Microsoft System Center Configuration Manager for software deployment, Windows Admin Center for server management, Remote Desktop Services for efficient support delivery, and PowerShell scripting for automation, this structured approach reduces unplanned downtime, ensures consistent system performance, and enables Education Office staff to focus on their training mission. Our proactive monitoring identifies potential problems before they impact operations, reducing emergency support requests by an estimated 40%.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.3 - Hyper-V - FLOWING PROSE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.3 Hyper-V Virtual Machine Management (PWS 10l)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] brings extensive Microsoft Hyper-V expertise to manage the Education Office's virtualized infrastructure. "),
        new TextRun({ text: "Per PWS Section 10l", bold: true }),
        new TextRun(", we administer virtual machines running Windows Server 2016, Small Business Server 2011, Ubuntu Linux 12, and Windows 11. Our Hyper-V administration methodology ensures high availability and optimal resource utilization through structured procedures for VM provisioning (standardized templates with proper security baselines), resource management (regular monitoring and optimization of CPU, memory, and storage allocation), snapshot management (controlled checkpoints with automated cleanup), and backup integration (daily VM-level backups with weekly full backups and monthly test restorations).")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Using Hyper-V Manager for daily administration, Windows Admin Center for unified management, Veeam Backup & Replication for data protection, and System Center Virtual Machine Manager for advanced scenarios, proper virtualization management maximizes hardware investment, enables rapid disaster recovery, and provides flexibility for future growth while protecting against data loss through comprehensive backup procedures.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.4 - WI-FI - FLOWING PROSE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.4 Enterprise WI-FI Network Management (PWS 10k)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] delivers expert management of the Education Office's Ubiquiti Enterprise WI-FI network. "),
        new TextRun({ text: "Per PWS Section 10k", bold: true }),
        new TextRun(", we ensure reliable wireless connectivity for all Education Office personnel and mobile devices. Our WI-FI management methodology focuses on reliability, security, and performance optimization, using the Ubiquiti UniFi Controller to maintain centralized visibility and control over all access points.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Key activities include daily monitoring (controller dashboard review for connection issues, interference, and client problems), security management (regular firmware updates, WPA3 configuration, rogue AP detection, guest network isolation), performance optimization (channel management, power level adjustment, client band steering), and capacity planning (usage trend analysis, access point placement optimization). Using Ubiquiti UniFi Controller for centralized management, UniFi mobile app for rapid on-site troubleshooting, WI-FI analyzer tools for spectrum management, and RADIUS integration for enterprise authentication, reliable WI-FI connectivity enables mobile learning, supports iPad classroom initiatives, and provides flexibility for Education Office operations.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.5 - Apple - FLOWING PROSE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.5 Apple Device and Server Management (PWS 10k)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] provides comprehensive Apple ecosystem management for the Education Office's macOS server, iPad, and iPod devices. "),
        new TextRun({ text: "Per PWS Section 10k", bold: true }),
        new TextRun(", we ensure seamless integration of Apple devices within the DoD environment. Our Apple management approach leverages Mobile Device Management (MDM) to maintain security compliance while enabling the flexibility Apple devices provide in educational settings.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Key activities include server administration (macOS Server maintenance, Open Directory management, profile distribution), MDM management (device enrollment, app deployment, configuration profile management, remote lock/wipe capability), device support (iPad/iPod troubleshooting, iOS updates, app installation, accessory support), and integration (Active Directory integration, network authentication, shared storage access). Using Jamf Pro for enterprise MDM management, Apple Business Manager for device enrollment, Apple School Manager integration for educational features, and Profile Manager for configuration deployment, effective Apple device management enables modern classroom technology while maintaining DoD security requirements.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.6 - Linux/Signage - FLOWING PROSE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.6 Linux and Digital Signage Administration (PWS 10j)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] manages the Linux-based Stinova DMS5 digital signage network supporting Education Office communications. "),
        new TextRun({ text: "Per PWS Section 10j", bold: true }),
        new TextRun(", we ensure reliable operation of this critical information display system. Our Linux administration approach applies enterprise-grade practices to the digital signage infrastructure, including server maintenance (Ubuntu Linux patching, service monitoring, log review, performance optimization), signage management (content scheduling, display configuration, network connectivity verification), and integration (network authentication, content source connectivity, scheduling system integration).")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Using SSH for secure remote administration, systemd for service management, Stinova DMS5 management interface, and Nagios/Zabbix for monitoring, reliable digital signage provides critical communications capability for the Education Office, displaying schedules, announcements, and emergency information.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.7 - Backup - FLOWING PROSE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.7 Data Backup and Recovery (PWS 10d)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] implements a comprehensive data safeguarding program to protect Education Office information assets. "),
        new TextRun({ text: "Per PWS Section 10d", bold: true }),
        new TextRun(", we design and administer backup procedures that ensure business continuity and regulatory compliance. Our backup strategy follows the industry-standard 3-2-1 rule: three copies of data, on two different media types, with one copy offsite.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("The backup schedule includes critical servers (daily incremental, 30-day retention via Veeam), user files (daily, 90-day retention via shadow copies plus backup), system state (weekly full, 1-year retention via image-based backup), and offsite copies (weekly encrypted transfer to secondary site). Recovery procedures include documented recovery for all critical systems, Recovery Time Objective (RTO) of 4 hours for critical systems, Recovery Point Objective (RPO) of 24 hours maximum data loss, and quarterly restoration testing with documented results. Using Veeam Backup & Replication, Windows Server Backup, shadow copies, and encrypted offsite replication, robust backup procedures protect against data loss from hardware failure, ransomware, or human error.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.8 - Security - FLOWING PROSE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.8 Information Security (PWS 10i, SS-4)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] maintains rigorous information security across all Education Office systems. "),
        new TextRun({ text: "Per PWS Section 10i and Service Summary SS-4", bold: true }),
        new TextRun(", we implement comprehensive security controls with a zero-defect performance standard. Our security program aligns with NIST 800-171 requirements and addresses "),
        new TextRun({ text: "DFARS 252.204-7008", bold: true }),
        new TextRun(" (CUI safeguarding) and "),
        new TextRun({ text: "DFARS 252.204-7012", bold: true }),
        new TextRun(" (cyber incident reporting).")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Security controls include access control (least privilege implementation, regular access reviews, MFA enforcement), audit and accountability (centralized logging, regular log review, anomaly detection), configuration management (security baselines, change control, vulnerability scanning), incident response (documented procedures, 72-hour DoD reporting capability, evidence preservation), and system protection (endpoint protection, host-based firewall, application whitelisting). "),
        new TextRun({ text: "Per DOD 5200.1-R and AFI 31-401", bold: true }),
        new TextRun(", we deliver security awareness training to Education Office personnel covering phishing recognition, CUI handling requirements, removable media policies, and incident reporting procedures. Using Microsoft Defender for Endpoint, Tenable for vulnerability management, Splunk for log aggregation, and KnowBe4 for security awareness training, comprehensive security protects Education Office data and maintains DoD compliance.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.9 - Emergency Response - FLOWING PROSE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.9 Emergency Response Capability (PWS 3)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] guarantees 2-hour emergency response capability for mission-critical situations. "),
        new TextRun({ text: "Per PWS Section 3", bold: true }),
        new TextRun(", when mission requirements prevent 7-day advance scheduling, our technician responds within 2 hours. Our on-call program ensures rapid response through a primary contact (assigned technician carries duty phone during non-duty hours), escalation path (documented escalation to backup technician and management), remote capability (VPN access enables immediate remote troubleshooting), and on-site response (technician within 2-hour travel time of Spangdahlem AB).")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Response procedures include COR contact to duty technician via phone/text, initial remote assessment within 15 minutes, on-site arrival within 2 hours if required, issue resolution and documentation, and follow-up during normal duty hours. Using mobile duty phone, VPN client for secure remote access, remote desktop tools, and mobile ticketing app, guaranteed emergency response ensures Education Office mission continuity even during unexpected technology failures.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.10 - Physical Security - FLOWING PROSE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.10 Physical Security and Key Control (PWS 6, SS-2)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] maintains strict physical security and key control procedures. "),
        new TextRun({ text: "Per PWS Sections 6h and 6i and Service Summary SS-2", bold: true }),
        new TextRun(", we safeguard all government property and maintain key accountability with zero defects. Property safeguarding includes current inventory maintained and reconciled monthly, equipment secured in locked areas when unattended, high-value items tracked with asset tags, and immediate reporting of lost/damaged property.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Key control includes key sign-out log maintained with date/time/purpose, keys secured in locked cabinet when not in use, no key duplication under any circumstances, and immediate reporting of lost keys to COR. Lock combination procedures include access limited to authorized personnel, combinations changed upon personnel departure, and secure storage of combination records. Using asset tracking database, key control logs, and security containers, strict physical security protects government investment and maintains operational security.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.11 - QA - FLOWING PROSE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.11 Quality Assurance and Reporting (PWS 5)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] supports COR oversight through comprehensive quality assurance and reporting. "),
        new TextRun({ text: "Per PWS Section 5", bold: true }),
        new TextRun(", we maintain documentation that enables effective contract surveillance. Daily documentation includes work activities logged in ticketing system, hours tracked in 4-hour increments, and tasks documented with resolution details. Weekly reporting includes summary of completed work orders, system status and availability metrics, and outstanding issues and planned activities. Monthly deliverables include completed timesheets per CLIN requirements, performance metrics against SS-1 through SS-4, and equipment inventory updates.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Using ServiceNow for ticketing and time tracking, SharePoint for document management, and Excel for performance metrics reporting, transparent reporting provides the COR with clear visibility into contractor performance, enabling effective oversight and early identification of any issues requiring attention.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.12 - Compliance - FLOWING PROSE
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.12 Regulatory Compliance (PWS 4)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] maintains full compliance with all applicable DoD, Air Force, and installation regulations. "),
        new TextRun({ text: "Per PWS Section 4", bold: true }),
        new TextRun(", we adhere to DoD Directives, Air Force Instructions, and local policies governing IT operations at Spangdahlem Air Base. Compliance areas include DOD 5200.1-R (Information Security Program), AFI 31-401 (Information Security Program Management), AFI 17-Series (Cyberspace Operations), DODI 8500.01 (Cybersecurity), and local installation policies and procedures.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Full regulatory compliance ensures Education Office IT operations meet all DoD standards, minimizing audit findings and maintaining security posture appropriate for the Air Force environment.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.13 - New System Implementation (PWS 10b)
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.13 New System Implementation (PWS 10b)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] delivers rapid implementation of new hardware and software systems. "),
        new TextRun({ text: "Per PWS Section 10b", bold: true }),
        new TextRun(", we implement new systems within one month of receipt from the government. Our implementation methodology includes initial assessment and compatibility verification within 48 hours, development of implementation plan with timeline and milestones, staged deployment with testing at each phase, user training and documentation, and final validation with COR sign-off.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Using standardized deployment checklists, imaging tools for rapid workstation setup, and change management procedures aligned with ITIL best practices, this structured approach ensures new technology is operational quickly while minimizing disruption to Education Office operations and maintaining security compliance throughout the implementation process.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.14 - Network Architecture Support (PWS 10c)
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.14 Network Architecture Support (PWS 10c)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] provides comprehensive network architecture support for the Education Office infrastructure. "),
        new TextRun({ text: "Per PWS Section 10c", bold: true }),
        new TextRun(", we maintain and optimize network connectivity, addressing LAN/WAN configuration, switch management, VLAN segmentation, firewall rule maintenance, and network performance monitoring. Our network support includes troubleshooting connectivity issues, optimizing traffic flow, and ensuring proper integration between wired and wireless networks.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Using network monitoring tools, packet analyzers for troubleshooting, and documentation standards for network diagrams, reliable network architecture ensures seamless connectivity for all Education Office systems, supporting both administrative and classroom technology requirements.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.15 - Asset Tracking and Documentation (PWS 10e)
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.15 Asset Tracking and Documentation (PWS 10e)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] maintains comprehensive asset tracking and facility documentation. "),
        new TextRun({ text: "Per PWS Section 10e", bold: true }),
        new TextRun(", we administer tracking systems and maintain current facility diagrams showing equipment locations, network drops, and infrastructure components. Our tracking approach includes maintaining an asset database with serial numbers, locations, and assignment information, updating facility diagrams when equipment moves or changes, conducting quarterly inventory reconciliation, and providing asset reports as requested by the COR.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Using asset management software, Visio or equivalent for facility diagrams, and barcode/asset tag systems, accurate asset tracking protects government investment, supports accountability requirements, and enables efficient planning for technology refresh cycles.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.16 - Data Migration and Database Maintenance (PWS 10f)
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.16 Data Migration and Database Maintenance (PWS 10f)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] performs data migration and database maintenance to ensure data integrity and system performance. "),
        new TextRun({ text: "Per PWS Section 10f", bold: true }),
        new TextRun(", we handle data migrations between systems, database optimization, and ongoing maintenance. Our approach includes pre-migration data validation and backup, structured migration with integrity checks, post-migration verification and user acceptance testing, and ongoing database maintenance including index optimization and space management.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Using database management tools, migration utilities, and data validation scripts, proper data migration and maintenance ensures Education Office data remains accurate, accessible, and performs optimally across all applications.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.17 - Technology Recommendations (PWS 10g)
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.17 Technology Recommendations (PWS 10g)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] provides proactive technology recommendations to support Education Office planning. "),
        new TextRun({ text: "Per PWS Section 10g", bold: true }),
        new TextRun(", we advise on future technology needs, upgrade paths, and emerging solutions that could benefit operations. Our advisory services include identifying end-of-life systems requiring replacement, recommending technology upgrades aligned with DoD standards, evaluating new solutions for potential adoption, and providing input for budget planning cycles.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Drawing on industry knowledge, vendor relationships, and understanding of DoD technology roadmaps, our recommendations help the Education Office stay current with technology while maximizing return on investment and maintaining security compliance.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.18 - IT Research and Procurement Support (PWS 10h)
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.18 IT Research and Procurement Support (PWS 10h)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] supports IT research and procurement activities for the Education Office. "),
        new TextRun({ text: "Per PWS Section 10h", bold: true }),
        new TextRun(", we assist with researching technology solutions, evaluating vendor options, and supporting purchase decisions. Our support includes researching products meeting specific requirements, comparing vendor offerings and pricing, providing technical specifications for procurement requests, and evaluating compatibility with existing infrastructure.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Using vendor resources, product databases, and technical evaluation criteria, our research support ensures the Education Office makes informed procurement decisions that meet mission requirements while remaining cost-effective and compliant with DoD acquisition guidelines.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.19 - SMART Board Administration (PWS 10m)
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.19 SMART Board Administration (PWS 10m)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] administers SMART Technologies interactive display systems supporting Education Office training capabilities. "),
        new TextRun({ text: "Per PWS Section 10m", bold: true }),
        new TextRun(", we maintain SMART boards including hardware troubleshooting, software updates, calibration, and user support. Our SMART board support includes regular calibration and touch accuracy verification, SMART Notebook software updates and licensing, connectivity troubleshooting (HDMI, USB, network), and user training on interactive features.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Using SMART diagnostic tools, firmware update utilities, and AV troubleshooting procedures, properly maintained SMART boards enable effective interactive instruction, enhancing the Education Office's training delivery capabilities.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 2.20 - Additional Support Services (PWS 10n)
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.20 Additional Support Services (PWS 10n)")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] provides flexibility to address additional critical support requirements as they arise. "),
        new TextRun({ text: "Per PWS Section 10n", bold: true }),
        new TextRun(", we respond to other technology support needs that may emerge during contract performance. Our flexible support approach includes assessing new requirements as they arise, providing recommendations for addressing emerging needs, coordinating with the COR on scope and priorities, and delivering support within the contracted labor hours.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("This flexibility ensures the Education Office receives comprehensive technology support even as requirements evolve, maintaining mission effectiveness throughout the contract period while staying within the defined scope of IT support services.")
      ]}),
      new Paragraph({ children: [new PageBreak()] }),

      // ============ VOLUME 3: PRICE EXHIBIT ============
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Volume 3: Price Exhibit")] }),

      // Section 3.1
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Price Summary")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("[COMPANY NAME] provides the following firm-fixed-price proposal for Education & Training Office Technology Support Services. "),
        new TextRun({ text: "Per SOL evaluation criteria", bold: true }),
        new TextRun(", the Total Evaluated Price (TEP) represents the sum of the Base Year, all Option Years, and the 6-Month Extension Option.")
      ]}),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "CLIN Pricing", bold: true, underline: {} })] }),
      new Paragraph({ children: [] }),

      // Pricing table
      createPricingTable(),
      new Paragraph({ children: [] }),

      new Paragraph({ children: [new TextRun({ text: "Total Evaluated Price Calculation", bold: true, underline: {} })] }),
      new Paragraph({ children: [] }),
      createTEPTable(),
      new Paragraph({ children: [new PageBreak()] }),

      // Section 3.2
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 Price Assumptions")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Pricing based on 220 units (4-hour blocks) per year as specified in PWS Section 3")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Work hours: 0800-1600 Monday through Friday (excludes US Federal holidays)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Emergency response (2-hour) included in unit price")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("All labor categories loaded with applicable benefits, overhead, and profit")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Pricing remains firm for duration of each contract period")] }),
      new Paragraph({ children: [new PageBreak()] }),

      // ============ ATTACHMENTS ============
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Attachments")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Attachment A: Key Personnel Resume(s)", bold: true })] }),
      new Paragraph({ children: [new TextRun("[Insert detailed resume(s) demonstrating 5+ years in each required skill area]")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Attachment B: Certification Copies", bold: true })] }),
      new Paragraph({ children: [new TextRun("[Insert copies of relevant certifications: Security+ CE, Network+, A+, Azure, Ubiquiti, Apple, etc.]")] }),
      new Paragraph({ children: [] }),
      new Paragraph({ children: [new TextRun({ text: "Attachment C: Past Performance Questionnaires", bold: true })] }),
      new Paragraph({ children: [new TextRun("[If required by solicitation]")] }),
    ]
  }]
});

// Helper function to create pricing table
function createPricingTable() {
  const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "000000" };
  const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

  return new Table({
    columnWidths: [1200, 3200, 800, 1600, 1400, 1600],
    rows: [
      new TableRow({
        tableHeader: true,
        children: ["CLIN", "Description", "Qty", "Unit", "Unit Price", "Extended Price"].map(text =>
          new TableCell({
            borders: cellBorders,
            shading: { fill: "D9D9D9", type: ShadingType.CLEAR },
            children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text, bold: true, size: 20 })] })]
          })
        )
      }),
      ...[
        ["0001", "Base Year IT Support", "220", "EA (4-hr)", "$[XXX.XX]", "$[XX,XXX.XX]"],
        ["1001", "Option Year 1", "220", "EA (4-hr)", "$[XXX.XX]", "$[XX,XXX.XX]"],
        ["2001", "Option Year 2", "220", "EA (4-hr)", "$[XXX.XX]", "$[XX,XXX.XX]"],
        ["3001", "Option Year 3", "220", "EA (4-hr)", "$[XXX.XX]", "$[XX,XXX.XX]"],
        ["4001", "Option Year 4", "220", "EA (4-hr)", "$[XXX.XX]", "$[XX,XXX.XX]"],
        ["X001", "6-Month Extension", "110", "EA (4-hr)", "$[XXX.XX]", "$[XX,XXX.XX]"]
      ].map(row => new TableRow({
        children: row.map(text =>
          new TableCell({
            borders: cellBorders,
            children: [new Paragraph({ children: [new TextRun({ text, size: 20 })] })]
          })
        )
      }))
    ]
  });
}

// Helper function to create TEP table
function createTEPTable() {
  const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "000000" };
  const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

  return new Table({
    columnWidths: [5000, 3000],
    rows: [
      new TableRow({
        tableHeader: true,
        children: ["Component", "Amount"].map(text =>
          new TableCell({
            borders: cellBorders,
            shading: { fill: "D9D9D9", type: ShadingType.CLEAR },
            children: [new Paragraph({ children: [new TextRun({ text, bold: true, size: 20 })] })]
          })
        )
      }),
      ...[
        ["Base Year (CLIN 0001)", "$[XX,XXX.XX]"],
        ["Option Year 1 (CLIN 1001)", "$[XX,XXX.XX]"],
        ["Option Year 2 (CLIN 2001)", "$[XX,XXX.XX]"],
        ["Option Year 3 (CLIN 3001)", "$[XX,XXX.XX]"],
        ["Option Year 4 (CLIN 4001)", "$[XX,XXX.XX]"],
        ["6-Month Extension (CLIN X001)", "$[XX,XXX.XX]"]
      ].map(row => new TableRow({
        children: row.map(text =>
          new TableCell({
            borders: cellBorders,
            children: [new Paragraph({ children: [new TextRun({ text, size: 20 })] })]
          })
        )
      })),
      new TableRow({
        children: [
          new TableCell({
            borders: cellBorders,
            shading: { fill: "D9D9D9", type: ShadingType.CLEAR },
            children: [new Paragraph({ children: [new TextRun({ text: "TOTAL EVALUATED PRICE", bold: true, size: 20 })] })]
          }),
          new TableCell({
            borders: cellBorders,
            shading: { fill: "D9D9D9", type: ShadingType.CLEAR },
            children: [new Paragraph({ children: [new TextRun({ text: "$[XXX,XXX.XX]", bold: true, size: 20 })] })]
          })
        ]
      })
    ]
  });
}

// Generate and save the document
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("C:\\Users\\sabaa\\OneDrive\\Desktop\\TEST_AGENTS\\PROPOSAL_TEAM\\outputs\\FA560625Q2038_Proposal_Draft_v3.docx", buffer);
  console.log("Document created successfully: FA560625Q2038_Proposal_Draft_v3.docx");
}).catch(err => {
  console.error("Error creating document:", err);
});
