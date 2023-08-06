from unittest import TestCase
from orkg import ORKG
from tempfile import NamedTemporaryFile


class TestPapers(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    orkg = ORKG()

    def test_add(self):
        paper = {"predicates": [], "paper": {
            "title": "Open Research Knowledge Graph: Next Generation Infrastructure for Semantic Scholarly Knowledge",
            "doi": "10.1145/3360901.3364435",
            "authors": [{"label": "Mohamad Yaser Jaradeh"}, {"label": "Allard Oelen"}, {"label": "Kheir Eddine Farfar"},
                        {"label": "Manuel Prinz"}, {"label": "Jennifer D'Souza"}, {"label": "Gábor Kismihók"},
                        {"label": "Markus Stocker"}, {"label": "Sören Auer"}], "publicationMonth": "",
            "publicationYear": 2019,
            "publishedIn": "Proceedings of the 10th International Conference on Knowledge Capture  - K-CAP '19",
            "researchField": "R11", "contributions": [{"name": "Contribution 1", "values": {"P32": [
                {"@temp": "_5254e420-ae9a-13ef-1c18-e716b9ea5c2b", "label": "Similarity measures", "class": "Problem",
                 "values": {}}], "P3": [
                {"text": "    Find similar research contributions inside the ORKG and suggest them to the user"}],
                "P1": [{
                    "@temp": "_851da0a6-7e83-c276-8df3-f66d0a680b30",
                    "label": "TF/iDF",
                    "values": {
                        "P2": [
                            {
                                "text": "Term frequency, inverse document frequency technique"
                            }
                        ]
                    }
                }
                ]
            }}]}}
        res = self.orkg.papers.add(params=paper)
        self.assertTrue(res.succeeded)

    def test_add_csv(self):
        csv_content = """paper:title,paper:authors,paper:doi,paper:publication_month,paper:publication_year,paper:research_field,contribution:research_problem,R0 estimates (average),95% Confidence interval,resource:Location,Study date,mean time interval between onset and hospital quarantine,Methods,mean incubation period,mean serial interval,study period name,Approaches,data collection tool,measurement condition 1,measurement condition 2,common symptoms,mean of serial interval,standard deviation of serial interval,code,incubation SD,incubation period mean,scenario,dataset description
Characterizing the transmission and identifying the control strategy for COVID-19 through epidemiological modeling,Ke K. Zhang; Linglin Xie; Lauren Lawless; Huijuan Zhou; Guannan Gao; Chengbin Xue,10.1101/2020.02.24.20026773,2,2020,R57,COVID-19 reproductive number,5.5,5.3-5.8,Mainland of China,,12.5 days,Monte carlo simulation,,,,,,,,,,,,,,,
Transmission interval estimates suggest pre-symptomatic spread of COVID-19,Lauren Tindale; Michelle Coombe; Jessica E Stockdale; Emma Garlock; Wing Yin Venus Lau; Manu Saraswat; Yen-Hsiang Brian Lee; Louxin Zhang; Dongxuan Chen; Jacco Wallinga; Caroline Colijn,10.1101/2020.03.03.20029983,3,2020,R57,COVID-19 reproductive number,1.97,1.45-2.48,Singapore,2020-01-19/2020-02-26,,,"7.1 (6.13, 8.25) days","4.56 (2.69, 6.42) days",,,,,,,,,,,,,
Transmission interval estimates suggest pre-symptomatic spread of COVID-19,Lauren Tindale; Michelle Coombe; Jessica E Stockdale; Emma Garlock; Wing Yin Venus Lau; Manu Saraswat; Yen-Hsiang Brian Lee; Louxin Zhang; Dongxuan Chen; Jacco Wallinga; Caroline Colijn,10.1101/2020.03.03.20029983,3,2020,R57,COVID-19 reproductive number,1.87,1.65-2.09,"Tianjin, China",2020-01-21/2020-02-27,,,"9 (7.92, 10.2) days","4.22 (3.43, 5.01) days",,,,,,,,,,,,,
"""
        csv_file = NamedTemporaryFile(mode="w", delete=False)
        csv_file.write(csv_content)
        csv_path = csv_file.name
        csv_file.close()

        res = self.orkg.papers.add_csv(file=csv_path)
        self.assertTrue(res.succeeded)
        self.assertTrue(len(res.content) == 3)
