import { useEffect, useState } from 'react';
import { View, Text, ScrollView } from 'react-native';
import { styles } from '../../assets/my-styles';

const BASE_URL = 'https://cs-webapps.bu.edu/alcobb/cs412/dadjokes';

export default function JokeListScreen() {
  const [jokes, setJokes] = useState<any[]>([]);

  useEffect(() => {
    fetch(`${BASE_URL}/api/jokes`)
      .then(res => res.json())
      .then(data => setJokes(data.results || data));
  }, []);

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.titleText}>All Dad Jokes</Text>
      {jokes.map(joke => (
        <View key={joke.id} style={styles.jokeCard}>
          <Text style={styles.jokeText}>{joke.text}</Text>
          <Text style={styles.contributorText}>— {joke.contributor}</Text>
        </View>
      ))}
    </ScrollView>
  );
}