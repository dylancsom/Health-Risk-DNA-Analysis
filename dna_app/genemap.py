import re

snps = []
    
with open("mydna.txt", "r") as file:
    for line in file:
        match = re.search(r'rs\w+', line)
        if match:
            rsid = match.group()
            alleles = line.split()
            alleles.remove(rsid)
            alleles = [x for x in alleles if not x.isdigit()]
            allele_str = ' '.join(alleles)
                
            match_chromosome = re.search(r'\b\d{1,2}\b', line)
            if match_chromosome:
                chromosome = match_chromosome.group()
            else: 
                chromosome = None
                
            position = re.findall(r'\d+', line)
            position = [x for x in position if len(x) <= 2 and x != chromosome]
            
            snps.append((rsid, chromosome, allele_str, position))
                
matches = []