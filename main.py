import os
import guitarpro

def merge_gp5_files(input_files, output_file):
    """
    Merge multiple Guitar Pro 5 files into a single GP5 file.
    
    Args:
        input_files (list): List of paths to input GP5 files
        output_file (str): Path where the merged file will be saved
    """
    if not input_files:
        raise ValueError("No input files provided")
    
    try:
        merged_song = guitarpro.parse(input_files[0])
        merged_song.title = "Setlist - " + merged_song.title
        merged_song.version = "FICHIER GUITAR PRO v5.00"
    except Exception as e:
        raise Exception(f"Error loading first file {input_files[0]}: {str(e)}")
    
    for file_path in input_files[1:]:
        try:
            current_song = guitarpro.parse(file_path)
            
            # Ensure track alignment: If a song has no tracks, add an empty one
            if not current_song.tracks:
                empty_track = guitarpro.models.Track(merged_song, 1)
                current_song.tracks.append(empty_track)
            
            # Insert a double bar line before adding new measures
            if len(merged_song.tracks[0].measures) > 0:
                last_measure = merged_song.tracks[0].measures[-1]
                last_measure.header.isDoubleBar = True
            
            # Ensure tempo changes are added correctly
            for measure in current_song.tracks[0].measures:
                if measure.header.tempo:
                    tempo = guitarpro.models.Tempo(value=measure.header.tempo.value)
                    measure.header.tempo = tempo
                    
            # Merge tracks properly
            for track_idx, track in enumerate(current_song.tracks):
                if track_idx < len(merged_song.tracks):
                    merged_song.tracks[track_idx].measures.extend(track.measures)
                else:
                    merged_song.tracks.append(track)
            
            # Add a text marker to indicate song separation
            first_new_measure = len(merged_song.tracks[0].measures) - len(current_song.tracks[0].measures)
            if first_new_measure >= 0:
                measure = merged_song.tracks[0].measures[first_new_measure]
                text = guitarpro.models.Text()
                text.value = f"--- {current_song.title} ---"
                measure.text = text
            
        except Exception as e:
            print(f"Warning: Error processing {file_path}: {str(e)}")
            continue
    
    try:
        if not output_file.lower().endswith('.gp5'):
            output_file = output_file.rsplit('.', 1)[0] + '.gp5'
            
        guitarpro.write(merged_song, output_file)
        print(f"Successfully created merged file: {output_file}")
    except Exception as e:
        raise Exception(f"Error saving merged file: {str(e)}")

if __name__ == "__main__":
    folder_path = "setlist_songs/"
    
    gp5_files = [
        os.path.join(folder_path, f) 
        for f in os.listdir(folder_path) 
        if f.lower().endswith('.gp5')
    ]
    
    gp5_files.sort()
    
    try:
        merge_gp5_files(gp5_files, "merged_setlist.gp5")
    except Exception as e:
        print(f"Error: {str(e)}")