def get_id_to_system_info(nlp, df_untok):
    id_to_system_info = {}
    for _, row in df_untok.iterrows():
        sid = row['sentence_order']
        doc = nlp(row['text'])
        sys_tokens = [word.text for sentence in doc.sentences for word in sentence.words]
        offsets = []
        curr = 0
        for t in sys_tokens:
            start = curr
            end = start + len(t)
            offsets.append((start, end))
            curr = end 
            
        id_to_system_info[sid] = {
            "tokens": sys_tokens, 
            "offsets": offsets
        }
    return id_to_system_info

def get_untokenized_data_split(test_df, train_df,  id_to_system_info):
    first_sid = test_df.iloc[0]["sentence_id"]
    last_sid = test_df.iloc[-1]["sentence_id"]
    test_formatted_data = []
    unique_test_sids = test_df["sentence_id"].unique()
    for sid in unique_test_sids:
        sys_data = id_to_system_info[sid]
        is_split_start = (sid == first_sid) and (sid in train_df["sentence_id"].values)
        is_split_end = (sid == last_sid) and (sid in train_df["sentence_id"].values)

        if is_split_start:
            gold_in_train = train_df[train_df["sentence_id"] == sid]["words"].tolist()
            chars_to_skip = sum(len(w) for w in gold_in_train)
            chunk = [t for t, (s, e) in zip(sys_data["tokens"], sys_data["offsets"]) if s >= chars_to_skip]
            test_formatted_data.append(chunk)

        elif is_split_end:
            gold_in_test = test_df[test_df["sentence_id"] == sid]["words"].tolist()
            chars_to_keep = sum(len(w) for w in gold_in_test)
            chunk = [t for t, (s, e) in zip(sys_data["tokens"], sys_data["offsets"]) if e <= chars_to_keep]
            test_formatted_data.append(chunk)

        else:
            test_formatted_data.append(sys_data["tokens"])
    return test_formatted_data