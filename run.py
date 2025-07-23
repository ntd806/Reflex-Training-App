from graphviz import Digraph

# Tạo mind map dưới dạng sơ đồ cây (tree diagram)
mind_map = Digraph(format='pdf')
mind_map.attr(rankdir='LR', size='10')

# Root
mind_map.node('root', 'HỌC TEMPLATE HIỆU QUẢ')

# Nhánh chính
mind_map.node('same', '✅ PHẦN GIỐNG NHAU')
mind_map.node('diff', '❌ PHẦN KHÁC NHAU')
mind_map.node('tips', '🧠 CÁCH HỌC THÔNG MINH')
mind_map.edges([('root', 'same'), ('root', 'diff'), ('root', 'tips')])

# Các nhánh con của PHẦN GIỐNG NHAU
mind_map.node('intro_same', 'Intro: This essay will discuss...')
mind_map.node('link_same', 'Liên kết: Moreover, For example...')
mind_map.node('reason_same', 'Lý do: This is because...')
mind_map.node('example_same', 'Ví dụ: For instance...')
mind_map.node('conclusion_same', 'Kết luận: In conclusion...')
for n in ['intro_same', 'link_same', 'reason_same', 'example_same', 'conclusion_same']:
    mind_map.edge('same', n)

# Các nhánh con của PHẦN KHÁC NHAU
mind_map.node('agree', 'Dạng 1: Agree/Disagree')
mind_map.node('discuss', 'Dạng 2: Discuss Both Views')
mind_map.node('problem', 'Dạng 3: Problem-Solution')
mind_map.edges([('diff', 'agree'), ('diff', 'discuss'), ('diff', 'problem')])

# Agree/Disagree
mind_map.node('agree_intro', 'Intro: I completely agree...')
mind_map.node('agree_b1', 'Body 1: The most compelling reason...')
mind_map.node('agree_b2', 'Body 2: Another convincing reason...')
mind_map.node('agree_con', 'Conclusion: I firmly support...')
mind_map.edges([('agree', 'agree_intro'), ('agree', 'agree_b1'), ('agree', 'agree_b2'), ('agree', 'agree_con')])

# Discuss Both
mind_map.node('discuss_intro', 'Intro: Examine both perspectives...')
mind_map.node('discuss_b1', 'Body 1: On the one hand...')
mind_map.node('discuss_b2', 'Body 2: On the other hand...')
mind_map.node('discuss_con', 'Conclusion: I personally believe...')
mind_map.edges([('discuss', 'discuss_intro'), ('discuss', 'discuss_b1'), ('discuss', 'discuss_b2'), ('discuss', 'discuss_con')])

# Problem-Solution
mind_map.node('problem_intro', 'Intro: This is a serious issue...')
mind_map.node('problem_b1', 'Body 1: One major problem is...')
mind_map.node('problem_b2', 'Body 2: One possible solution is...')
mind_map.node('problem_con', 'Conclusion: Measures can mitigate...')
mind_map.edges([('problem', 'problem_intro'), ('problem', 'problem_b1'), ('problem', 'problem_b2'), ('problem', 'problem_con')])

# Tips
mind_map.node('fixed_phrases', '🧩 Học câu cố định dùng mọi dạng')
mind_map.node('compare_table', '🧠 Tạo bảng 3 cột: Agree/Discuss/Problem')
mind_map.node('practice_all', '🔁 Luyện 1 đề theo 3 dạng')
mind_map.edges([('tips', 'fixed_phrases'), ('tips', 'compare_table'), ('tips', 'practice_all')])

# Xuất file PDF
mind_map.render('mindmap_ielts_template', cleanup=True)
